from typing import List

from ..base.llm import OpenAIClient
from ..types.runtime_config import RuntimeConfig

vllm_runtime = RuntimeConfig(
    api_key='vllm',
    base_url='http://localhost:8000/v1',
    models=[
        'Qwen2.5-7B-Instruct',
        'Qwen2.5-0.5B-Instruct',
        'Qwen2.5-VL-7B-Instruct',
    ]
)


class VLLM(OpenAIClient):
    def __init__(
            self,
            api_key: str = vllm_runtime.api_key,
            base_url: str = vllm_runtime.base_url,
            models: List = vllm_runtime.models,
            default_model: str = vllm_runtime.models[0],
            **kwargs
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            models=models,
            default_model=default_model,
            **kwargs
        )


