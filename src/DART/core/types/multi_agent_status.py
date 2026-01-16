from datetime import datetime
from typing import List, Dict, Any

from .runtime_config import RuntimeConfig
from ..task import Task, TaskStatus
from ..base.data_class import DataClass


class MultiAgentRunTimeStatus(DataClass):
    """多Agent运行时状态管理类"""

    def __init__(self, runtime_config: RuntimeConfig = None):
        super().__init__()
        self.runtime_config = runtime_config
        self.tasks: Dict[str, Task] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.dag_status = "not_started"  # not_started, running, completed, failed
        self.start_time = None
        self.end_time = None
        self.active_tasks: List[str] = []
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []

    def add_task(self, task: Task) -> None:
        """添加任务"""
        self.tasks[task.task_id] = task

    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs) -> None:
        """更新任务状态"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        old_status = task.status
        task.status = status

        # 记录状态变化
        status_change = {
            "task_id": task_id,
            "agent_name": task.agent.name if task.agent else None,
            "old_status": old_status.value if old_status else None,
            "new_status": status.value,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.task_history.append(status_change)

        # 更新活跃/完成/失败任务列表
        if status == TaskStatus.RUNNING:
            if task_id not in self.active_tasks:
                self.active_tasks.append(task_id)
        elif status == TaskStatus.COMPLETED:
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            if task_id not in self.completed_tasks:
                self.completed_tasks.append(task_id)
        elif status == TaskStatus.FAILED:
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            if task_id not in self.failed_tasks:
                self.failed_tasks.append(task_id)

    def start_execution(self) -> None:
        """开始执行"""
        self.dag_status = "running"
        self.start_time = datetime.now()

    def end_execution(self, status: str = "completed") -> None:
        """结束执行"""
        self.dag_status = status
        self.end_time = datetime.now()

    def get_task_status_summary(self) -> Dict[str, Any]:
        """获取任务状态摘要"""
        total = len(self.tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        active = len(self.active_tasks)
        pending = total - completed - failed - active

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "active": active,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0
        }

    def get_execution_time(self) -> float:
        """获取执行时间（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "runtime_config": self.runtime_config.to_dict() if self.runtime_config else None,
            "dag_status": self.dag_status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.get_execution_time(),
            "task_summary": self.get_task_status_summary(),
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "task_history": self.task_history
        }