import unittest
from unittest.mock import patch

# 假设导入路径正确，并且这些类在项目中是可用的
from DART.core.types.message import Message, SystemMessage, UserMessage, AssistantMessage, ToolMessage
from DART.core.types.role import Role


class TestMessage(unittest.TestCase):

    def test_message_initialization(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = Message(
                role='system',
                author='AuthorName',
                persona='Persona',
                description='A description',
                content='Message content',
                refusal='Refusal message',
                thinking='Thinking process'
            )
            self.assertEqual(message.role, 'system')
            self.assertEqual(message.author, 'AuthorName')
            self.assertEqual(message.persona, 'Persona')
            self.assertEqual(message.description, 'A description')
            self.assertEqual(message.content, 'Message content')
            self.assertEqual(message.refusal, 'Refusal message')
            self.assertEqual(message.thinking, 'Thinking process')

    def test_message_invalid_role(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            with self.assertRaises(ValueError):
                Message(role='invalid_role')

    def test_is_empty(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = Message(role='system')
            self.assertTrue(message.is_empty())

            message.content = 'Some content'
            self.assertFalse(message.is_empty())

    def test_to_dict(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = Message(role='system', content='Message content')
            message_dict = message.to_dict()
            self.assertIsInstance(message_dict, dict)

    def test_to_string(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = Message(role='system', content='Message content')
            message_str = message.to_string()
            self.assertIsInstance(message_str, str)

    def test_to_json(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = Message(role='system', content='Message content')
            message_json = message.to_json()
            self.assertIsInstance(message_json, dict)

    def test_system_message_initialization(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = SystemMessage(content='System content')
            self.assertEqual(message.role, 'system')
            self.assertEqual(message.content, 'System content')

    def test_user_message_initialization(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = UserMessage(content='User content')
            self.assertEqual(message.role, 'user')
            self.assertEqual(message.content, 'User content')

    def test_assistant_message_initialization(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = AssistantMessage(content='Assistant content', name='Assistant')
            self.assertEqual(message.role, 'assistant')
            self.assertEqual(message.author, 'Assistant')
            self.assertEqual(message.content, 'Assistant content')

    def test_tool_message_initialization(self):
        with patch.object(Role, 'values', return_value=['system', 'user', 'assistant', 'tool']):
            message = ToolMessage(content='Tool content', name='Tool')
            self.assertEqual(message.role, 'tool')
            self.assertEqual(message.author, 'Tool')
            self.assertEqual(message.content, 'Tool content')


if __name__ == '__main__':
    unittest.main()
