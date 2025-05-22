from .constant import Constant


# clients related
DEFAULT_API_KEY = Constant(value='ollama').value
DEFAULT_ORGANIZATION = Constant(value=None).value
DEFAULT_PROJECT = Constant(value=None).value
DEFAULT_BASE_URL = Constant(value='http://localhost:11434/v1').value
DEFAULT_WEBSOCKET_BASE_URL = Constant(value=None).value
DEFAULT_MAX_RETRIES = Constant(value=2).value
DEFAULT_TIMEOUT = Constant(value=60).value
DEFAULT_HTTP_CLIENT = Constant(value=None).value

DEFAULT_MAX_CHAT_TIMES = Constant(value=10).value
