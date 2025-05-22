from typing import List, Dict

from ..base.data_class import DataClass
from ..constants.configs import (
    DEFAULT_ORGANIZATION,
    DEFAULT_PROJECT,
    DEFAULT_WEBSOCKET_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_HTTP_CLIENT,
)


class RuntimeConfig(DataClass):
    def __init__(
            self,
            api_key: str,
            base_url: str,
            organization: str | None = DEFAULT_ORGANIZATION,
            project: str | None = DEFAULT_PROJECT,
            websocket_base_url: str | None = DEFAULT_WEBSOCKET_BASE_URL,
            timeout: float | None = DEFAULT_TIMEOUT,
            max_retries: int = DEFAULT_MAX_RETRIES,
            default_headers: Dict[str, str] | None = None,
            default_query: Dict[str, object] | None = None,
            http_client: str | None = DEFAULT_HTTP_CLIENT,
            models: List[str] | None = None,
            default_model: str | None = None,
    ):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.organization = organization
        self.project = project
        self.websocket_base_url = websocket_base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        self.default_query = default_query or {}
        self.http_client = http_client
        self.models = models or []
        self.default_model = default_model

    def to_dict(self, include_none=False) -> Dict:
        return super().to_dict(include_none=False)
