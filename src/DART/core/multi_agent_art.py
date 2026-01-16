import copy
from typing import List, Dict, Any, Generator, Optional, Callable

from .art import ART
from .dag_scheduler import DAGScheduler
from .base.agent import Agent
from .constants.configs import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, DEFAULT_MAX_CHAT_TIMES
from .types.chat_config import ChatConfig
from .types.message import SystemMessage, AssistantMessage, UserMessage
from .types.multi_agent_status import MultiAgentRunTimeStatus
from .types.runtime_config import RuntimeConfig
from .task import Task, TaskStatus
from ..utils.logger import logger


class MultiAgentART:
    """多Agent运行时环境，支持DAG调度和并行执行"""

    def __init__(
        self,
        runtime_config: RuntimeConfig,
        chat_config: Optional[ChatConfig] = None,
        max_workers: int = 4
    ):
        """
        初始化多Agent运行时环境

        Args:
            runtime_config: 运行时配置
            chat_config: 聊天配置
            max_workers: 最大并行执行的工作线程数
        """
        if not isinstance(runtime_config, RuntimeConfig):
            raise ValueError("runtime_config must be an instance of RuntimeConfig")

        self.runtime_config = runtime_config
        self.chat_config = chat_config if isinstance(chat_config, ChatConfig) else ChatConfig()

        if not self.chat_config.model:
            self.chat_config.model = self.runtime_config.default_model

        # 创建单Agent ART实例，用于执行单个Agent
        self.single_agent_art = ART(runtime_config, chat_config)

        # DAG调度器
        self.scheduler = DAGScheduler(max_workers=max_workers)

        # 多Agent状态管理
        self.status = MultiAgentRunTimeStatus(runtime_config)

    def add_task(
        self,
        task_id: str,
        agent: Agent,
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        timeout: Optional[float] = None
    ) -> None:
        """
        添加Agent任务

        Args:
            task_id: 任务唯一标识符
            agent: Agent实例
            dependencies: 依赖的任务ID列表
            inputs: 任务输入数据
            priority: 任务优先级
            timeout: 任务执行超时时间
        """
        task = Task(
            task_id=task_id,
            agent=agent,
            dependencies=dependencies,
            inputs=inputs,
            priority=priority,
            timeout=timeout
        )
        self.scheduler.add_task(task)
        self.status.add_task(task)

    def add_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """
        批量添加任务

        Args:
            tasks: 任务配置列表，每个任务包含task_id, agent等字段
        """
        for task_config in tasks:
            self.add_task(**task_config)

    def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        执行单个Agent任务

        Args:
            task: 要执行的任务

        Returns:
            任务执行结果
        """
        try:
            logger.info(f"Executing task: {task.task_id} with agent: {task.agent.name}")

            # 准备消息
            messages = []
            if task.inputs and 'messages' in task.inputs:
                messages = task.inputs['messages']
            elif task.inputs and 'user_message' in task.inputs:
                messages = [UserMessage(content=task.inputs['user_message'])]

            # 执行Agent
            result_content = ""
            chat_config = task.inputs.get('chat_config', self.chat_config)
            max_chat_times = task.inputs.get('max_chat_times', DEFAULT_MAX_CHAT_TIMES)

            for chunk in self.single_agent_art.run(
                agent=task.agent,
                messages=messages,
                chat_config=chat_config,
                max_chat_times=max_chat_times,
                stream=False  # 多Agent环境下不使用流式输出
            ):
                if 'content' in chunk and isinstance(chunk['content'], str):
                    result_content += chunk['content']

            return {
                'task_id': task.task_id,
                'agent_name': task.agent.name,
                'content': result_content,
                'success': True
            }

        except Exception as e:
            logger.error(f"Task {task.task_id} execution failed: {str(e)}")
            return {
                'task_id': task.task_id,
                'agent_name': task.agent.name,
                'error': str(e),
                'success': False
            }

    def run(
        self,
        messages: Optional[List] = None,
        global_inputs: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        运行多Agent系统

        Args:
            messages: 全局消息列表
            global_inputs: 全局输入参数
            **kwargs: 额外参数

        Yields:
            执行状态和结果
        """
        try:
            # 验证DAG
            if not self.scheduler.validate_dag():
                yield {'error': 'Invalid DAG: cycle detected or missing dependencies'}
                return

            # 开始执行
            self.status.start_execution()
            yield {'multi_agent_status': 'start', 'total_tasks': len(self.scheduler.tasks)}

            # 执行DAG调度
            for dag_event in self.scheduler.run(self.execute_task):
                # 更新状态
                if 'task_started' in dag_event:
                    task_id = dag_event['task_started']
                    self.status.update_task_status(task_id, TaskStatus.RUNNING)

                elif 'task_completed' in dag_event:
                    task_id = dag_event['task_completed']
                    result = dag_event['result']
                    self.status.update_task_status(
                        task_id,
                        TaskStatus.COMPLETED,
                        result=result
                    )

                elif 'task_failed' in dag_event:
                    task_id = dag_event['task_failed']
                    error = dag_event['error']
                    self.status.update_task_status(
                        task_id,
                        TaskStatus.FAILED,
                        error=error
                    )

                # 传递DAG事件
                yield dag_event

            # 结束执行
            if self.status.failed_tasks:
                self.status.end_execution("completed_with_errors")
                yield {'multi_agent_status': 'completed_with_errors'}
            else:
                self.status.end_execution("completed")
                yield {'multi_agent_status': 'completed'}

        except Exception as e:
            logger.error(f"MultiAgent execution failed: {str(e)}")
            self.status.end_execution("failed")
            yield {'error': f'MultiAgent execution failed: {str(e)}'}

    def get_status(self) -> Dict[str, Any]:
        """获取当前运行状态"""
        return {
            'scheduler_status': self.scheduler.get_task_status(),
            'multi_agent_status': self.status.to_dict()
        }

    def reset(self) -> None:
        """重置运行环境"""
        self.scheduler.reset()
        self.status = MultiAgentRunTimeStatus(self.runtime_config)

    def get_task_results(self) -> Dict[str, Any]:
        """获取所有任务的执行结果"""
        results = {}
        for task_id, task in self.status.tasks.items():
            results[task_id] = {
                'status': task.status.value,
                'outputs': task.outputs,
                'error_message': task.error_message,
                'execution_time': (
                    (task.end_time - task.start_time).total_seconds()
                    if task.start_time and task.end_time else None
                )
            }
        return results