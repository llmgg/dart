import unittest
from unittest.mock import Mock

from openai.types.chat.chat_completion_chunk import ChoiceDelta

from DART.core.models.local_models import LocalModels
from DART.core.types.choice import Choice
from DART.utils.tool_utils import create_tool_desc


def get_whether(city: str):
    """
    获取天气信息
    @param city:
    @return:
    """
    return f"the whether of '{city}': sunny"


def get_hotel(city: str, price: float = 100):
    """
    获取酒店信息
    @param city
    @param price:
    @return:
    """
    return f"the city: {city}\nthe price: {price}"


class TestChoice(unittest.TestCase):

    def setUp(self):
        self.choice = Choice()
        self.llm = LocalModels()

    def test_streaming_response(self):
        """测试参数合并逻辑"""
        test_params = {
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'temperature': 0.7,
            'debug': True,
        }
        generator = self.llm.create_chat_completion(**test_params)
        content = ''
        for delta in generator:
            self.choice.merge_delta(delta)
            content += delta.content
            print(delta)
        print(self.choice.to_string(include_none=True))
        self.assertFalse(self.choice.is_empty())
        self.assertEqual(self.choice.content, content)
        self.choice.content = ''
        self.assertTrue(self.choice.is_empty())

    def test_tool_call(self):
        self.llm = LocalModels(default_model='qwen2.5:7b', timeout=300)
        tools = [create_tool_desc(get_whether, index=1), create_tool_desc(get_hotel, index=2)]
        test_params = {
            'messages': [{'role': 'user', 'content': '给我推荐北京的天气和一个三百元以内的酒店。'}],
            'temperature': 1.0,
            '__tools__': tools,
            'debug': True,
        }
        generator = self.llm.create_chat_completion(**test_params)
        for delta in generator:
            self.choice.merge_delta(delta)
            print(delta)
        print(self.choice.to_string(include_none=True))
        print(self.choice)

    def test_merge_delta_with_partial_update(self):
        # 初始状态
        self.choice.content = 'initial content'
        self.choice.refusal = 'initial refusal'

        # 模拟一个部分更新的 ChoiceDelta
        delta = Mock(spec=ChoiceDelta)
        delta.role = None
        delta.content = ' and more'
        delta.refusal = ' updated'
        delta.thinking = None
        delta.tool_calls = []

        # 调用 merge_delta 方法
        self.choice.merge_delta(delta)

        # 验证属性是否正确更新
        self.assertEqual(self.choice.content, 'initial content and more')
        self.assertEqual(self.choice.refusal, 'initial refusal updated')


if __name__ == '__main__':
    unittest.main()
