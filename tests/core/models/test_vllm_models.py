import unittest

from openai import OpenAI

from DART.core.models.vllm_models import VLLM
from DART.core.types.choice import Choice
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
        self.llm = VLLM()

    def test_initialization(self):
        """测试初始化参数是否正确"""
        self.assertEqual(self.llm.api_key, 'vllm')
        self.assertEqual(self.llm.base_url, 'http://localhost:8000/v1')
        self.assertEqual(self.llm.default_model, 'Qwen2.5-7B-Instruct')
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
        choice = Choice()
        generator = self.llm.create_chat_completion(**test_params)
        for delta in generator:
            choice.merge_delta(delta)
            print(delta)
        print(choice.to_dict())

    def test_sys_prompt(self):
        tools = [create_tool_desc(get_whether)]
        test_params = {
            'messages': [
                {'role': 'system', 'content': '你是一个工具调用专家，请根据用户的问题选择合适的工具进行调用'},
                {'role': 'user', 'content': '今天北京天气怎么样？'},
            ],
            'model': self.llm.default_model,
            'temperature': 0.7,
            'tools': tools,
            'debug': True,
        }
        choice = Choice()
        generator = self.llm.create_chat_completion(**test_params)
        for delta in generator:
            choice.merge_delta(delta)
            print(delta)
        print(choice.to_dict())


if __name__ == '__main__':
    unittest.main()

