from typing import List, Dict

from ..base.data_class import DataClass


class ChatConfig(DataClass):
    def __init__(
            self,
            model: str | None = None,
            frequency_penalty: float | None = None,
            logit_bias: Dict[str, int] | None = None,
            logprobs: bool | None = None,
            max_completion_tokens: int | None = None,
            max_tokens: int | None = None,
            n: int | None = None,
            presence_penalty: float | None = None,
            seek: int | None = None,
            stop: str | List[str] | None = None,
            temperature: float | None = None,
            tool_choice: str | None = None,
            top_logprobs: int | None = None,
            top_p: float | None = None,
            timeout: float | None = None,
    ):
        super().__init__()
        self.model = model
        self.frequency_penalty = frequency_penalty
        self.logit_bias = logit_bias
        self.logprobs = logprobs
        self.max_completion_tokens = max_completion_tokens
        self.max_tokens = max_tokens
        self.n = n
        self.presence_penalty = presence_penalty
        self.seek = seek
        self.stop = stop
        self.temperature = temperature
        self.tool_choice = tool_choice
        self.top_logprobs = top_logprobs
        self.top_p = top_p
        self.timeout = timeout

    def to_dict(self, include_none=False) -> Dict:
        return super().to_dict(include_none=include_none)
