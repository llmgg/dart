from typing import Optional, Dict

from openai.types.chat.chat_completion_chunk import ChoiceDelta, ChoiceDeltaToolCall, ChoiceDeltaToolCallFunction

from .role import Role
from ..base.data_class import DataClass, valid_str


class ToolCallFunction(DataClass):
    def __init__(self, name: str = None, arguments: str = None):
        self.name = name
        self.arguments = arguments


class ToolCall(DataClass):
    def __init__(self, index: int = None, id: str = None, type: str = None, function: ToolCallFunction = None):
        self.index = index
        self.id = id
        self.type = type
        self.function = function


class Choice(DataClass):
    def __init__(
            self,
            role: Optional[str] = None,
            content: Optional[str] = None,
            tool_calls: Optional[Dict[int, ToolCall]] = None,
            refusal: Optional[str] = None,
            thinking: Optional[str] = None,
    ):
        super().__init__()
        self.role = role
        self.content = content or ''
        self.tool_calls = tool_calls or {}
        self.refusal = refusal or ''
        self.thinking = thinking or ''

    def merge_delta(self, delta: ChoiceDelta):
        if not isinstance(delta, ChoiceDelta):
            return

        if delta.role and delta.role in Role.values():
            self.role = delta.role
        if isinstance(delta.content, str):
            self.content += delta.content
        if isinstance(delta.refusal, str):
            self.refusal += delta.refusal
        if hasattr(delta, 'thinking') and isinstance(delta.thinking, str):
            self.thinking += delta.thinking
        if delta.tool_calls:
            tool_calls = {
                self._key_of_tool(tool): tool
                for tool in delta.tool_calls if isinstance(tool, ChoiceDeltaToolCall)
            }
            for key, tool in tool_calls.items():
                if key in self.tool_calls:
                    if isinstance(tool.id, str) and tool.id:
                        self.tool_calls[key].id += tool.id
                    if isinstance(tool.function, ChoiceDeltaToolCallFunction):
                        if isinstance(tool.function.name, str):
                            self.tool_calls[key].function.name += tool.function.name
                        if isinstance(tool.function.arguments, str):
                            self.tool_calls[key].function.arguments += tool.function.arguments
                    if isinstance(tool.type, str) and tool.type:
                        self.tool_calls[key].type += tool.type
                else:
                    new_tool = ToolCall(index=tool.index, id=tool.id, type=tool.type)
                    new_tool.function = ToolCallFunction(name='', arguments='')
                    if isinstance(tool.function, ChoiceDeltaToolCallFunction):
                        new_tool.function.name = valid_str(tool.function.name)
                        new_tool.function.arguments = valid_str(tool.function.arguments)
                    self.tool_calls[self._key_of_tool(tool)] = new_tool

    def split_thinking_from_content(self):
        if '<think>' in self.content and '</think>' in self.content:
            is_content = False
        else:
            is_content = True
        thinking = []
        content = []
        for line in self.content.split('\n'):
            line = line.strip()
            if is_content:
                content.append(line)
            else:
                thinking.append(line)
            if '</think>' in line and len(line) < 10:
                is_content = True
        self.thinking = '\n'.join(thinking)
        self.content = '\n'.join(content)

    @staticmethod
    def _key_of_tool(tool: ChoiceDeltaToolCall):
        # return '_'.join(
        #     [
        #         "index", str(tool.index) if tool.index is not None else '',
        #         'id', str(tool.id) if tool.id is not None else '',
        #     ]
        # )
        return tool.index

    def is_empty(self) -> bool:
        return (not self.content) and (not self.tool_calls) and (not self.thinking)
