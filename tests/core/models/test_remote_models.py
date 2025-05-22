import unittest

from DART.core.models.remote_models import RemoteModels


class TestLocalModels(unittest.TestCase):

    def setUp(self):
        self.llm = RemoteModels()
        # self.llm = RemoteModels(default_model='default_model')

    def test_create_stream_chat_completion(self):
        """测试创建聊天完成"""
        messages = [
            {
                'role': 'user',
                'content': '你好',
            }
        ]
        response = self.llm.create_stream_chat_completion(messages=messages, model=self.llm.default_model)
        for item in response:
            print(item)


if __name__ == '__main__':
    unittest.main()
