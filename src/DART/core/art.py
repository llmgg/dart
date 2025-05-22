import copy
from typing import List, Dict, Any, Generator, Optional

from .base.agent import Agent
from .base.llm import OpenAIClient
from .constants.configs import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, DEFAULT_MAX_CHAT_TIMES
from .types.chat_config import ChatConfig
from .types.choice import Choice
from .types.message import SystemMessage, AssistantMessage, ToolMessage, UserMessage
from .types.role import Role
from .types.runtime_config import RuntimeConfig
from .types.status import AgentRunTimeStatus
from .types.tool_result import ToolResult, ToolResultType
from ..utils.formatter import to_str_format
from ..utils.logger import logger
from ..utils.tool_utils import create_tool_desc


class ART:
    """Agent Runtime环境，负责执行Agent并管理运行时状态"""

    def __init__(self, runtime_config: RuntimeConfig, chat_config: Optional[ChatConfig] = None):
        """
        初始化Agent Runtime环境

        Args:
            runtime_config: 运行时配置
            chat_config: 聊天配置

        Raises:
            ValueError: 如果runtime_config不是RuntimeConfig实例
        """
        if not isinstance(runtime_config, RuntimeConfig):
            raise ValueError("runtime_config must be an instance of RuntimeConfig")

        self.runtime_config = runtime_config
        self.chat_config = chat_config if isinstance(chat_config, ChatConfig) else ChatConfig()

        if not self.chat_config.model:
            self.chat_config.model = self.runtime_config.default_model

        self.client = OpenAIClient(
            api_key=self.runtime_config.api_key,
            base_url=self.runtime_config.base_url,
            models=self.runtime_config.models or [],
            default_model=self.runtime_config.default_model or '',
            max_retries=self.runtime_config.max_retries or DEFAULT_MAX_RETRIES,
            timeout=self.runtime_config.timeout or DEFAULT_TIMEOUT,
        )
        self.status = AgentRunTimeStatus(runtime_config=self.runtime_config)

    def run(
            self,
            agent: Agent,
            messages: List,
            chat_config: Optional[ChatConfig] = None,
            max_chat_times: int = DEFAULT_MAX_CHAT_TIMES,
            share_tool_results: bool = True,
            stop_if_no_tools: bool = True,
            include_think: bool = False,
            stream: bool = True,
            **kwargs
    ):
        """
        运行Agent处理消息

        Args:
            agent: 要运行的Agent实例
            messages: 消息列表
            chat_config: 聊天配置
            max_chat_times: 最大对话次数
            share_tool_results: 是否共享工具结果
            stop_if_no_tools: 如果没有工具可用，是否停止运行
            include_think: 是否在回复的内容中包含思考过程
            stream: 是否使用流式输出
            **kwargs: 额外参数

        Yields:
            运行状态和结果

        Raises:
            ValueError: 如果agent不是Agent实例或结果类型不正确
        """
        if not isinstance(agent, Agent):
            raise ValueError(f"agent must be an instance of Agent, but got {type(agent)}")
        debug = kwargs.get('debug', False)
        self.status.current_agent = agent

        # 初始化运行时环境
        history = copy.deepcopy(messages)
        sys_mess = SystemMessage(content=create_system_prompt(agent))
        assi_mess = AssistantMessage(content='', name=agent.name, persona=agent.persona)
        chat_args = self._prepare_chat_args(agent, chat_config)
        chat_args['tools'] = [create_tool_desc(tool) for tool in agent.tools() if callable(tool)]

        tool_messages = []
        tool_err_info = []
        tools_called = []
        chat_times = 0

        yield {'runtime_status': 'start'}

        while chat_times < max_chat_times:
            chat_times += 1
            yield {'agent': f'{agent.name} -- {chat_times}'}
            logger.info(f'agent: {agent.name}\nchat_times: {chat_times}')

            # 更新消息和工具
            chat_args['messages'] = self._update_messages_and_tools(
                sys_mess, history, tool_messages, tool_err_info, assi_mess
            )

            if debug:
                self._log_debug_info(chat_args, tools_called)

            # 生成回复
            choice = Choice(role=Role.ASSISTANT.value, content='')
            for chunk in self._generate_choice(chat_args, choice):
                yield chunk
            choice.split_thinking_from_content()
            yield {'choice': choice}

            if debug:
                logger.info('Choice: \n' + to_str_format(choice.to_dict()))

            # 记录执行结果
            self.status.add_chat_history(chat_args=chat_args, choice=choice)

            # 回复为空，运行结束
            if choice.is_empty():
                break

            # 保存回复内容
            if choice.content or choice.thinking:
                if include_think:
                    assi_mess.content += choice.thinking + '\n' + choice.content
                else:
                    assi_mess.content += choice.content

            # 运行工具调用
            tools_recalled, tool_results = self._process_tool_calls(agent, choice)
            yield {'tools_recalled': tools_recalled}

            # 不用调用工具，运行结束
            if stop_if_no_tools and len(tools_recalled) == 0:
                break
            if not agent.execute_tools:
                break

            # 更新工具消息
            init_len = len(tool_messages)
            tool_messages, tool_err_info, tools_called = self._messages_from_tool_results(
                tool_results, tool_messages, tools_called, history, chat_config, max_chat_times,
                share_tool_results, stop_if_no_tools, include_think, stream, kwargs
            )

            # 有新的工具消息，重置回复内容
            if len(tool_messages) > init_len or len(tool_err_info) > 0:
                assi_mess.content = ''

        yield {'content': assi_mess.content}
        yield {'runtime_status': 'end'}

    def _prepare_chat_args(self, agent: Agent, chat_config: Optional[ChatConfig], stream: bool = True):
        """准备聊天参数，优先级如下：API > Agent > ART"""
        chat_args = {}
        if isinstance(self.chat_config, ChatConfig):  # runtime的聊天配置
            chat_args.update(self.chat_config.to_dict())
        if isinstance(agent.chat_config, ChatConfig):  # agent的聊天配置
            chat_args.update(agent.chat_config.to_dict())
        if isinstance(chat_config, ChatConfig):  # API的聊天配置
            chat_args.update(chat_config.to_dict())
        chat_args['stream'] = stream
        return chat_args

    @staticmethod
    def _update_messages_and_tools(
            sys_mess: SystemMessage,
            history: List,
            tool_messages: List,
            tool_err_info: List,
            assi_mess: AssistantMessage,
    ):
        """更新聊天纪录和工具列表"""
        messages = [sys_mess.to_message()] + history + tool_messages + tool_err_info
        if assi_mess.content:
            messages.append(assi_mess.to_message())
        return messages

    @staticmethod
    def _log_debug_info(chat_args: Dict[str, Any], tools_called: List[str]) -> None:
        """记录调试信息"""
        logger.info(f'tools_called: {tools_called}')
        logger.info(f'Chat Args:\n' + to_str_format(chat_args))

    def _generate_choice(self, chat_args: Dict[str, Any], choice: Choice, stream: bool = True) -> Generator:
        """生成选择"""
        if chat_args['model'] not in self.client.models:
            raise ValueError(
                f'model "{chat_args["model"]}" is not supported, the available models are: {self.client.models}'
            )
        chat_args['stream'] = stream
        if stream:
            for delta in self.client.create_chat_completion(**chat_args):
                yield {'delta': delta}
                choice.merge_delta(delta)
        else:
            chat_args['stream'] = True
            for delta in self.client.create_chat_completion(**chat_args):
                choice.merge_delta(delta)

    def _process_tool_calls(self, agent: Agent, choice: Choice) -> List:
        """处理工具调用"""
        tools_recalled = []
        tool_results = []
        if choice.tool_calls:
            tools_recalled = list(choice.tool_calls.values())
            if agent.execute_tools:
                if agent.parallel_execute:
                    tool_results = agent.run_tools_parallel(tools_recalled)
                else:
                    tool_results = agent.run_tools(tools_recalled)
                # 记录工具调用历史
                for tool_call, result in zip(tools_recalled, tool_results):
                    self.status.add_tool_calls_history(tool_call, result)
                    if not result.success:
                        self.status.add_tool_error_history(tool_call, result)
        return tools_recalled, tool_results

    def _messages_from_tool_results(
            self,
            tool_results: List[ToolResult],
            tool_messages: List,
            tools_called: List[str],
            history: List,
            chat_config: Optional[ChatConfig],
            max_chat_times: int,
            share_tool_results: bool,
            stop_if_no_tools: bool,
            include_think: bool,
            stream: bool,
            kwargs: Dict
    ):
        """更新工具消息"""
        tool_messages = copy.deepcopy(tool_messages)
        tools_called = copy.deepcopy(tools_called)
        tool_err_info = []
        for result in tool_results:
            if result.result_type == ToolResultType.STRING.value:
                tool_mess = ToolMessage(content=result.result_value, name=result.name, description=result.description)
                if result.success:
                    tools_called.append(result.name)
                    tool_messages.append(tool_mess.to_message())
                else:
                    tool_err_info.append(tool_mess)
            elif result.result_type == ToolResultType.AGENT.value:
                handoff = result.result_value
                if not isinstance(handoff, Agent):
                    raise ValueError(f"The returned value should be a Agent, but got {type(handoff)}")

                # 运行代理并获取内容
                content = self._run_handoff_agent(
                    handoff, history, tool_messages, share_tool_results, stop_if_no_tools, include_think,
                    chat_config, max_chat_times, stream, kwargs
                )

                if content:
                    tools_called.append(handoff.name)
                    tool_messages.append(
                        ToolMessage(content=content, name=handoff.name, description=handoff.persona).to_message()
                    )
            else:
                error_msg = f'Unknown result type: {result.result_type}'
                raise ValueError(error_msg)

        if tool_err_info:
            err_tools = [err_tool.name for err_tool in tool_err_info]
            tool_err_messages = [err_tool.to_message() for err_tool in tool_err_info]
            tool_err_messages.append(
                UserMessage(
                    content=f'根据上下文的聊天内容以及调用工具时返回的错误信息, 重新修正调用工具时所使用的参数（例如，参数内容和参数格式等），重新调用下面列表中的工具：{err_tools}',
                ).to_message()
            )
        else:
            tool_err_messages = []

        return tool_messages, tool_err_messages, tools_called

    def _run_handoff_agent(
            self,
            handoff: Agent,
            history: List,
            tool_messages: List,
            share_tool_results: bool,
            stop_if_no_tools: bool,
            include_think: bool,
            chat_config: Optional[ChatConfig],
            max_chat_times: int,
            stream: bool,
            kwargs: Dict
    ) -> str:
        """运行handoff代理"""
        inner_art = handoff.art if isinstance(handoff.art, ART) else self
        inner_mess = history + tool_messages if share_tool_results else history

        content = ''
        for chunk in inner_art.run(
                agent=handoff,
                messages=inner_mess,
                chat_config=chat_config,
                max_chat_times=max_chat_times,
                share_tool_results=share_tool_results,
                stop_if_no_tools=stop_if_no_tools,
                include_think=False,
                stream=stream,
                **kwargs
        ):
            if 'content' in chunk and isinstance(chunk['content'], str):
                content += chunk['content']
        return content


def create_system_prompt(agent: Agent) -> str:
    """创建系统提示"""
    prompt = f"""
你是一个智能体，你的名称、角色定位、任务描述和注意事项如下，严格遵守这些信息的约束并完成用户的请求。

**【智能体名称】**
{agent.name}

**【角色定位】**
{agent.persona}

**【任务描述】**
{agent.description}

**【注意事项】**
基于智能体的【角色定位】与【任务描述】，按以下步骤处理用户的请求：
-. **理解用户意图**：结合上下文多轮对话的内容，理解用户当前对话轮次的真实意图。
-. **校验任务范围**：判断用户意图是否在智能体的【任务描述】范围内，只完成【任务描述】范围内的任务。
-. **检查工具调用**：检查与用户意图相关的所有工具是否均被调用并且正确返回，对未调用的相关工具进行调用。
-. **总结工具信息**：结合工具的功能描述信息，对工具的返回信息进行过滤和总结，只保留与工具功能相关的信息。
-. **检查输出内容**：输出内容只能包含该智能体【任务描述】范围内的内容，对范围外的内容不做任何输出和回答。
""".strip()
    return prompt
