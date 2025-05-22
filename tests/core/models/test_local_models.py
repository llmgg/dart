import unittest

from openai import OpenAI

from DART.core.models.local_models import LocalModels
from DART.utils.tool_utils import create_tool_desc


def get_whether(location: str):
    """
    获取天气信息
    @param location:
    @return:
    """
    return f"the whether of '{location}': sunny"


class TestLocalModels(unittest.TestCase):

    def setUp(self):
        self.llm = LocalModels()

    def test_initialization(self):
        """测试初始化参数是否正确"""
        self.assertEqual(self.llm.api_key, 'ollama')
        self.assertEqual(self.llm.base_url, 'http://localhost:11434/v1')
        self.assertIsInstance(self.llm.client, OpenAI)

    def test_invalid_client_type(self):
        """测试客户端类型验证"""
        self.llm.client = "invalid_client"
        with self.assertRaisesRegex(ValueError, "not an instance of OpenAI"):
            next(self.llm.create_chat_completion(messages=[], model=''))

    def test_streaming_response(self):
        """测试参数合并逻辑"""
        test_params = {
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'model': self.llm.default_model,
            'temperature': 0.7,
            'debug': True,
        }
        generator = self.llm.create_chat_completion(**test_params)
        for delta in generator:
            print(delta)

    def test_tool_call(self):
        tools = [create_tool_desc(get_whether)]
        test_params = {
            'messages': [{'role': 'user', 'content': '今天北京天气怎么样？'}],
            'model': self.llm.default_model,
            'temperature': 0.7,
            'tools': tools,
            'debug': True,
        }
        generator = self.llm.create_chat_completion(**test_params)
        for delta in generator:
            print(delta)


if __name__ == '__main__':
    unittest.main()
