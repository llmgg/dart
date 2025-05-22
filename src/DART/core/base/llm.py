import copy
from typing import Optional, List, Any

from openai import OpenAI

from ..constants.configs import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from ...utils.logger import logger, str_format


class LLM:
    def __init__(
            self,
            api_key: str | None = None,
            base_url: str | None = None,
            models: Optional[List[str]] = None,
            default_model: Optional[str] = None,
            max_retries: int = DEFAULT_MAX_RETRIES,
            timeout: float = DEFAULT_TIMEOUT,
            http_client: Any | None = None
    ):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.models = models or []
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout = timeout
        self.http_client = http_client
        self.client = http_client
        if self.default_model not in self.models:
            raise ValueError(f'''default_model should be one of {self.models}, but got '{self.default_model}'.''')

    def create_chat_completion(self, messages: list, model: str = None, tools: List = None, stream: bool = True,
                               **kwargs) -> Any:
        model = model or self.default_model
        if stream:
            return self.create_stream_chat_completion(messages, model, tools, **kwargs)
        else:
            return self.create_no_stream_chat_completion(messages, model, tools, **kwargs)

    def create_stream_chat_completion(self, messages: list, model: str, tools=None, **kwargs) -> Any:
        ...

    def create_no_stream_chat_completion(self, messages: list, model: str, tools=None, **kwargs) -> Any:
        ...

    def create_embedding(self, **kwargs) -> Any:
        ...


class OpenAIClient(LLM):
    def __init__(
            self,
            api_key: str,
            base_url: str,
            models: List | None = None,
            default_model: str | None = None,
            **kwargs
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            models=models,
            default_model=default_model,
            **kwargs
        )
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    def create_stream_chat_completion(
            self,
            messages: list,
            model: str,
            tools=None,
            max_tokens=None,
            temperature=None,
            tool_choice=None,
            timeout=None,
            **kwargs
    ):
        return self._llm_response(messages=messages, model=model, tools=tools, max_tokens=max_tokens,
                                  temperature=temperature, tool_choice=tool_choice, timeout=timeout,
                                  stream=True, **kwargs)

    def create_no_stream_chat_completion(
            self,
            messages: list,
            model: str,
            tools=None,
            max_tokens=None,
            temperature=None,
            tool_choice=None,
            timeout=None,
            **kwargs
    ):
        return self._llm_response(messages=messages, model=model, tools=tools, max_tokens=max_tokens,
                                  temperature=temperature, tool_choice=tool_choice, timeout=timeout,
                                  stream=False, **kwargs)

    def _llm_response(
            self,
            messages: list,
            model: str,
            tools=None,
            max_tokens=None,
            temperature=None,
            tool_choice=None,
            timeout=None,
            stream=True,
            **kwargs
    ):
        if not isinstance(self.client, OpenAI):
            raise ValueError("client is not an instance of OpenAI")

        chat_args = copy.deepcopy(kwargs)
        if messages:
            chat_args['messages'] = messages
        if model:
            chat_args['model'] = model
        if tools:
            chat_args['tools'] = tools
        if max_tokens:
            chat_args['max_tokens'] = max_tokens
        if temperature:
            chat_args['temperature'] = temperature
        if tool_choice:
            chat_args['tool_choice'] = tool_choice
        if timeout:
            chat_args['timeout'] = timeout

        debug = chat_args.pop('debug', False)
        if debug:
            logger.info('Chat Parameters: \n' + str_format(chat_args))

        try:
            if stream:
                chat_args['stream'] = True
                for chunk in self.client.chat.completions.create(**chat_args):
                    yield chunk.choices[0].delta
            else:
                chat_args['stream'] = False
                yield self.client.chat.completions.create(**chat_args).choices[0].message
        except Exception as e:
            logger.error(f'Error in getting chat completion from openai: {e}')
            return None
