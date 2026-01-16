from enum import Enum
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .base.data_class import DataClass

if TYPE_CHECKING:
    from .base.agent import Agent


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"        # 执行失败
    SKIPPED = "skipped"      # 被跳过


class Task(DataClass):
    """Agent任务类"""

    def __init__(
        self,
        task_id: str,
        agent: 'Agent',
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        初始化任务

        Args:
            task_id: 任务唯一标识符
            agent: 对应的Agent实例
            dependencies: 依赖的任务ID列表
            inputs: 任务输入数据
            outputs: 任务输出数据
            priority: 任务优先级，数字越大优先级越高
            timeout: 任务执行超时时间（秒）
            **kwargs: 其他参数
        """
        super().__init__()
        self.task_id = task_id
        self.agent = agent
        self.dependencies = dependencies or []
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.priority = priority
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.kwargs = kwargs

    def is_ready(self, completed_tasks: List[str]) -> bool:
        """检查任务是否准备就绪（所有依赖任务都已完成）"""
        return all(dep in completed_tasks for dep in self.dependencies)

    def can_run_parallel(self, running_tasks: List[str]) -> bool:
        """检查任务是否可以并行运行（没有正在运行的依赖任务）"""
        return not any(dep in running_tasks for dep in self.dependencies)

    def mark_running(self):
        """标记任务为运行状态"""
        from datetime import datetime
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()

    def mark_completed(self, outputs: Optional[Dict[str, Any]] = None):
        """标记任务为完成状态"""
        from datetime import datetime
        self.status = TaskStatus.COMPLETED
        self.end_time = datetime.now()
        if outputs:
            self.outputs.update(outputs)

    def mark_failed(self, error_message: str):
        """标记任务为失败状态"""
        from datetime import datetime
        self.status = TaskStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent.name if self.agent else None,
            "dependencies": self.dependencies,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "priority": self.priority,
            "timeout": self.timeout,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            **self.kwargs
        }