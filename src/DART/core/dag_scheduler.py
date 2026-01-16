import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List, Set, Optional, Callable, Any, Generator
from collections import defaultdict, deque

from .task import Task, TaskStatus
from ..utils.logger import logger


class DAGScheduler:
    """DAG调度器，负责管理和调度任务执行"""

    def __init__(self, max_workers: int = 4):
        """
        初始化DAG调度器

        Args:
            max_workers: 最大并行执行的工作线程数
        """
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: Set[str] = set()
        self.running_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._event = threading.Event()

    def add_task(self, task: Task) -> None:
        """添加任务到调度器"""
        if task.task_id in self.tasks:
            raise ValueError(f"Task {task.task_id} already exists")
        self.tasks[task.task_id] = task
        logger.info(f"Added task: {task.task_id}")

    def add_tasks(self, tasks: List[Task]) -> None:
        """批量添加任务"""
        for task in tasks:
            self.add_task(task)

    def get_ready_tasks(self) -> List[Task]:
        """获取准备就绪的任务（所有依赖都已完成且未运行）"""
        ready_tasks = []
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and
                task.is_ready(list(self.completed_tasks)) and
                task.task_id not in self.running_tasks):
                ready_tasks.append(task)
        return ready_tasks

    def get_executable_tasks(self) -> List[Task]:
        """获取可以并行执行的任务（准备就绪且没有正在运行的依赖）"""
        ready_tasks = self.get_ready_tasks()
        executable_tasks = []

        for task in ready_tasks:
            if task.can_run_parallel(list(self.running_tasks)):
                executable_tasks.append(task)

        # 按优先级排序，优先级高的先执行
        executable_tasks.sort(key=lambda t: t.priority, reverse=True)
        return executable_tasks

    def validate_dag(self) -> bool:
        """验证DAG是否有效（无环）"""
        # 使用拓扑排序检测环
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False

            visited.add(task_id)
            rec_stack.add(task_id)

            task = self.tasks[task_id]
            for dep in task.dependencies:
                if dep not in self.tasks:
                    logger.error(f"Dependency {dep} not found for task {task_id}")
                    return True
                if has_cycle(dep):
                    return True

            rec_stack.remove(task_id)
            return False

        for task_id in self.tasks:
            if has_cycle(task_id):
                return False
        return True

    def execute_task(self, task: Task, execute_func: Callable[[Task], Any]) -> Future:
        """执行单个任务"""
        def task_wrapper():
            try:
                with self._lock:
                    task.mark_running()
                    self.running_tasks.add(task.task_id)

                logger.info(f"Starting task: {task.task_id}")
                result = execute_func(task)

                with self._lock:
                    task.mark_completed(result)
                    self.completed_tasks.add(task.task_id)
                    self.running_tasks.remove(task.task_id)

                logger.info(f"Completed task: {task.task_id}")
                self._event.set()  # 通知调度器有任务完成
                return result

            except Exception as e:
                error_msg = f"Task {task.task_id} failed: {str(e)}"
                logger.error(error_msg)

                with self._lock:
                    task.mark_failed(str(e))
                    self.failed_tasks.add(task.task_id)
                    if task.task_id in self.running_tasks:
                        self.running_tasks.remove(task.task_id)

                self._event.set()
                raise e

        return self.executor.submit(task_wrapper)

    def run(self, execute_func: Callable[[Task], Any]) -> Generator[Dict[str, Any], None, None]:
        """
        运行DAG调度

        Args:
            execute_func: 任务执行函数，接收Task对象，返回执行结果

        Yields:
            调度状态信息
        """
        if not self.validate_dag():
            raise ValueError("Invalid DAG: cycle detected or missing dependencies")

        logger.info(f"Starting DAG execution with {len(self.tasks)} tasks")

        yield {'dag_status': 'start', 'total_tasks': len(self.tasks)}

        active_futures = []
        completed_count = 0

        while completed_count < len(self.tasks):
            # 获取可以执行的任务
            executable_tasks = self.get_executable_tasks()

            # 提交可执行任务
            for task in executable_tasks:
                if len(active_futures) < self.max_workers:
                    future = self.execute_task(task, execute_func)
                    active_futures.append((task.task_id, future))
                    yield {'task_started': task.task_id}

            # 检查已完成的任务
            still_active = []
            for task_id, future in active_futures:
                if future.done():
                    completed_count += 1
                    try:
                        result = future.result()
                        yield {'task_completed': task_id, 'result': result}
                    except Exception as e:
                        yield {'task_failed': task_id, 'error': str(e)}
                else:
                    still_active.append((task_id, future))

            active_futures = still_active

            # 如果没有活跃任务但还有未完成的任务，等待
            if not active_futures and completed_count < len(self.tasks):
                logger.info("Waiting for task completion...")
                self._event.wait(timeout=1.0)
                self._event.clear()

            # 小延迟避免忙等待
            if active_futures:
                time.sleep(0.1)

        self.executor.shutdown(wait=True)

        # 检查是否有失败的任务
        if self.failed_tasks:
            yield {'dag_status': 'completed_with_errors', 'failed_tasks': list(self.failed_tasks)}
        else:
            yield {'dag_status': 'completed'}

        logger.info("DAG execution finished")

    def get_task_status(self) -> Dict[str, Any]:
        """获取所有任务的状态"""
        return {
            'total': len(self.tasks),
            'completed': len(self.completed_tasks),
            'running': len(self.running_tasks),
            'failed': len(self.failed_tasks),
            'pending': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'tasks': {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        }

    def reset(self) -> None:
        """重置调度器状态"""
        self.completed_tasks.clear()
        self.running_tasks.clear()
        self.failed_tasks.clear()
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.start_time = None
            task.end_time = None
            task.error_message = None