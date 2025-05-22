from datetime import datetime
from typing import List, Dict, Any

from .choice import Choice, ToolCall
from .runtime_config import RuntimeConfig
from .tool_result import ToolResult, ToolResultType
from ..base.data_class import DataClass
from ...utils.formatter import to_str_format


class AgentRunTimeStatus(DataClass):
    """存储Agent运行时状态的类"""

    def __init__(self, runtime_config: RuntimeConfig = None):
        super().__init__()
        self.runtime_config = runtime_config
        self.chat_history = []
        self.current_agent = None
        self.tool_calls_history = []
        self.tool_error_history = []

    def add_chat_history(self, chat_args: Dict, choice: Choice) -> None:
        """记录代理执行信息"""
        self.chat_history.append({
            "agent": self.current_agent.name,
            "chat_args": to_str_format(chat_args),
            "choice": to_str_format(choice.to_dict()),
            "timestamp": datetime.now().isoformat()
        })

    def add_tool_calls_history(self, tool_call: ToolCall, tool_result: ToolResult) -> None:
        """记录工具调用信息"""
        self.tool_calls_history.append({
            "agent": self.current_agent.name,
            "tool": to_str_format(tool_call.to_dict()),
            "result": to_str_format(
                tool_result.to_dict()) if tool_result.result_type == ToolResultType.STRING.value else tool_result,
            "timestamp": datetime.now().isoformat()
        })

    def add_tool_error_history(self, tool_call: ToolCall, tool_result: ToolResult) -> None:
        """记录错误信息"""
        self.tool_error_history.append({
            "agent": self.current_agent.name,
            "tool": to_str_format(tool_call.to_dict()),
            "result": to_str_format(tool_result.to_dict()),
            "timestamp": datetime.now().isoformat()
        })

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.chat_history

    def get_tool_calls_history(self) -> List[Dict[str, Any]]:
        """获取工具调用历史"""
        return self.tool_calls_history

    def get_tool_error_history(self) -> List[Dict[str, str]]:
        """获取错误历史"""
        return self.tool_error_history
