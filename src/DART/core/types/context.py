from typing import Any, Dict, Optional

from .chat_config import ChatConfig
from .runtime_config import RuntimeConfig
from ..base.data_class import DataClass, valid_dict


class Context(DataClass):
    def __init__(
            self,
            runtime_config: Optional[RuntimeConfig] = None,
            chat_config: Optional[ChatConfig] = None,
            tool_args: Dict[str, Dict[str, Any]] | None = None,
            storage: Dict[str, Any] | None = None,
    ):
        super().__init__()
        '''runtime config for Agent Run Time'''
        self.runtime_config = runtime_config

        '''chat config for Agent'''
        self.chat_config = chat_config

        '''tool args for __tools__. tool.name is used as key, and tool.args is used as value'''
        self.tool_args = valid_dict(tool_args)

        '''other values stored in the context'''
        self.storage = valid_dict(storage)
