from typing import List

from ..base.llm import OpenAIClient
from ..types.runtime_config import RuntimeConfig

jd_runtime = RuntimeConfig(
    api_key='OpgnZ6YefnXez1QVmHUKjB6kdq4r5g2a',
    base_url='http://api.chatrhino.jd.com/api/v1',
    models=('Chatrhino-81B-Pro', 'Chatrhino-470B-preview-0103', 'Chatrhino-81B-T1'),
    default_model='Chatrhino-81B-Pro',
)


class RemoteModels(OpenAIClient):
    def __init__(
            self,
            api_key: str = jd_runtime.api_key,
            base_url: str = jd_runtime.base_url,
            models: List = jd_runtime.models,
            default_model: str = jd_runtime.default_model,
            **kwargs
    ):
        super().__init__(api_key, base_url, models, default_model, **kwargs)
