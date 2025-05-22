import enum
from typing import Any

from ..base.data_class import DataClass


class ToolResultType(enum.Enum):
    STRING = 'string'
    AGENT = 'agent'
    NONE = 'null'

    @classmethod
    def values(cls):
        return (member.value for member in cls)


class ToolResult(DataClass):
    """
    The Result returned by a tool.
    """

    """The name of the tool."""
    name: str

    """The description of the tool."""
    description: str

    """The value returned by the tool."""
    result_value: Any

    """The type of the result."""
    result_type: str

    """While True means the tool is executed successfully, False means the tool is not executed."""
    success: bool

    def __init__(self, name=None, description=None, result_value=None, result_type=ToolResultType.NONE.value,
                 success: bool = False):
        super().__init__()
        self.set_value(name=name, description=description, result_value=result_value, result_type=result_type)
        self.success = success

    def set_value(self, name, description, result_value, result_type):
        if result_type not in ToolResultType.values():
            raise ValueError(f"type must be one of {ToolResultType.values()}, but got '{result_type}'.")
        self.name = name
        self.description = description
        self.result_type = result_type
        if self.result_type == ToolResultType.STRING.value:
            if not isinstance(result_value, str):
                raise ValueError(f'result_value must be a string, but got: {type(result_value)}')
            self.result_value = result_value
        elif self.result_type == ToolResultType.AGENT.value:
            from ..base.agent import Agent
            if not isinstance(result_value, Agent):
                raise ValueError(f'result_value must be an Agent, but got: {type(result_value)}')
            self.result_value = result_value
        else:
            if result_value is not None:
                raise ValueError(f'result_value must be None, but got: {result_value}')
            self.result_value = None
