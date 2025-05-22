import json
from typing import Dict, Callable, Optional, List, Any

from .data_class import DataClass
from ..types.chat_config import ChatConfig
from ..types.choice import ToolCall
from ..types.context import Context
from ..types.dataset import DataSet
from ..types.memory import Memory
from ..types.tool_result import ToolResult, ToolResultType
from ...utils.create_tool import create_tool
from ...utils.multi_processes import multi_process_run


class Agent(DataClass):
    def __init__(
            self,
            name: str,
            persona: str | Callable,
            description: str | Callable,
            tools: Optional[List[Callable]] = None,
            handoffs: Optional[List['Agent']] = None,
            context: Optional[Context] = None,
            execute_tools: bool = True,
            parallel_execute: bool = False,
            datasets: Optional[Dict[str, DataSet]] = None,
            memory: Optional[Memory] = None,
            chat_config: Optional[ChatConfig] = None,
            ignore_handoffs: bool = False,
            ignore_tools: bool = False,
            art: Any = None,
            **kwargs
    ):
        super().__init__()
        """The name of the agent. It should be unique in a same agent runtime environment."""
        self.name = name

        """The short description of the agent."""
        if callable(persona):
            self.persona = persona()
        elif isinstance(persona, str):
            self.persona = persona
        else:
            self.persona = None

        """The long description of the agent, which will be used as system prompt."""
        if callable(description):
            self.description = description()
        elif isinstance(description, str):
            self.description = description
        else:
            self.description = None

        self.__tools__ = tools or []
        self.__handoffs__ = handoffs or []
        self.context = context
        self.execute_tools = execute_tools
        self.parallel_execute = parallel_execute
        self.datasets = datasets or {}
        self.memory = memory
        self.chat_config = chat_config
        self.ignore_handoffs = ignore_handoffs
        self.ignore_tools = ignore_tools
        self.art = art
        self.kwargs = kwargs

        # create tools mapping used in run_tool
        self.tools_mapping = {}
        self.handoffs_mapping = {}
        self.update_mapping()

    def transfer_handoffs_to_tools(self, excludes: List[str] = None) -> List[Callable]:
        excludes = excludes or []
        tools = [agent.to_tool() for agent in self.__handoffs__ if
                 isinstance(agent, Agent) and agent.name not in excludes]
        return [tool for tool in tools if callable(tool)]

    def tools(self, excludes: List[str] = None) -> List[Callable]:
        excludes = excludes or []
        tools = []
        if not self.ignore_tools:
            tools.extend(
                [tool for tool in self.__tools__ if callable(tool) and tool.__name__ not in excludes]
            )
        if not self.ignore_handoffs:
            tools.extend(
                [tool for tool in self.transfer_handoffs_to_tools(excludes)]
            )
        return tools

    def set_tools(self, tools: List[Callable]):
        self.__tools__ = [tool for tool in tools if callable(tool)]

    def add_tool(self, tool: Callable):
        if callable(tool):
            self.__tools__.append(tool)

    def set_handoffs(self, handoffs: List['Agent']):
        self.__handoffs__ = [agent for agent in handoffs if isinstance(agent, Agent)]

    def add_handoff(self, handoff: 'Agent'):
        if isinstance(handoff, Agent):
            self.__handoffs__.append(handoff)

    def update_mapping(self):
        self.tools_mapping = {
            tool.__name__: tool for tool in self.__tools__ if callable(tool)
        }
        self.handoffs_mapping = {
            tool.__name__: tool for tool in self.transfer_handoffs_to_tools()
        }

    def run_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        self.update_mapping()
        results = [self._run_tool_(tool) for tool in tool_calls]
        return results

    def run_tools_parallel(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        self.update_mapping()
        tool_results = multi_process_run(
            self._run_tool_, tool_calls, keep_order=True,
        )
        results = []
        for tool, result in zip(tool_calls, tool_results):
            if isinstance(result, str) and 'Executor Run Error' in result:
                result = ToolResult(
                    name=tool.function.name,
                    result_value=result,
                    result_type=ToolResultType.STRING.value,
                    success=False,
                )
            results.append(result)
        return results

    def _run_tool_(self, tool: ToolCall):
        func_name = tool.function.name
        if func_name in self.tools_mapping:
            func_args = tool.function.arguments
            func = self.tools_mapping[func_name]
            func_doc = func.__doc__
            try:
                func_result = func(**json.loads(func_args))
                return_status = True
            except Exception as e:
                func_result = '\n'.join(
                    [
                        "Tool Call Error:",
                        f"\t**Tool Name**: {func_name}",
                        f"\t**Arguments Used**: {func_args}",
                        f"\t**Error Information**: {e}"
                    ]
                )
                return_status = False
        elif func_name in self.handoffs_mapping:
            func = self.handoffs_mapping[func_name]
            func_doc = func.__doc__
            try:
                func_result = func()
                return_status = True
            except Exception as e:
                func_result = '\n'.join(
                    [
                        "Tool Call Error:",
                        f"**Tool Name**: \n{func_name}",
                        f"**Error Information**: \n{e}"
                    ]
                )
                return_status = False
        else:
            func_doc = f"Tool '{func_name}' is not found"
            func_result = '\n'.join(
                [
                    "Tool Call Error:",
                    f"**Tool Name**: \n{func_name}",
                    f"**Error Information**: \n{func_doc}"
                ]
            )
            return_status = False

        if isinstance(func_result, str):
            result = ToolResult(name=func_name, description=func_doc, result_value=func_result,
                                result_type=ToolResultType.STRING.value, success=return_status)
        elif isinstance(func_result, Agent):
            result = ToolResult(name=func_name, description=func_doc, result_value=func_result,
                                result_type=ToolResultType.AGENT.value, success=return_status)
        else:
            result = ToolResult(name=func_name, description=func_doc, result_value=None,
                                result_type=ToolResultType.NONE.value, success=return_status)
        return result

    def to_tool(self) -> Callable:
        return transfer_agent_to_tool(self)


def transfer_agent_to_tool(agent: Agent) -> Callable:
    def return_agent(handoff: Agent):
        return handoff

    if not isinstance(agent, Agent):
        raise ValueError(f'agent must be an Agent instance, but got {type(agent)}')

    doc = ''.join(
        [
            '调用该工具将返回一个Agent智能体，该智能体对应的角色定位和任务描述如下：\n',
            f'**角色定位**：\n{agent.persona}\n\n\n',
            f'**任务描述**：\n{agent.description}',
        ]
    )
    return create_tool(
        name=agent.name, doc=doc, api=return_agent, args={'handoff': agent},
    )
