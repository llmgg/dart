from typing import List

from ..base.llm import OpenAIClient
from ..types.runtime_config import RuntimeConfig

local_models = (
    'qwen3:30b-a3b',
    'qwen3:32b',
    'qwen3:8b',
    'qwen3:0.6b',
)

local_runtime = RuntimeConfig(
    api_key='ollama',
    base_url='http://localhost:11434/v1',
)


class LocalModels(OpenAIClient):
    def __init__(
            self,
            api_key: str = local_runtime.api_key,
            base_url: str = local_runtime.base_url,
            models: List = local_models,
            default_model: str = local_models[0],
            **kwargs
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            models=models,
            default_model=default_model,
            **kwargs
        )
