import unittest
from unittest.mock import MagicMock

from DART.core.types.status import AgentRunTimeStatus
from DART.core.base.agent import Agent
from DART.core.types.choice import Choice, ToolCall
from DART.core.types.tool_result import ToolResult
from DART.core.types.runtime_config import RuntimeConfig


class TestAgentRunTimeStatus(unittest.TestCase):

    def setUp(self):
        # Create a mock agent
        self.agent = MagicMock(spec=Agent)
        self.agent.name = "TestAgent"

        # Create a runtime config
        self.runtime_config = MagicMock(spec=RuntimeConfig)

        # Initialize the AgentRunTimeStatus
        self.runtime_status = AgentRunTimeStatus(runtime_config=self.runtime_config)
        self.runtime_status.current_agent = self.agent

    def test_add_chat_history(self):
        chat_args = {"key": "value"}
        choice = MagicMock(spec=Choice)
        choice.to_dict.return_value = {"mock": "choice"}

        # Add chat history
        self.runtime_status.add_chat_history(chat_args, choice)

        # Check if chat history is added correctly
        self.assertEqual(len(self.runtime_status.chat_history), 1)
        history_entry = self.runtime_status.chat_history[0]
        self.assertEqual(history_entry["agent"], "TestAgent")
        self.assertIn("key", history_entry["chat_args"])
        self.assertIn("mock", history_entry["choice"])
        self.assertIsInstance(history_entry["timestamp"], str)

    def test_add_tool_calls_history(self):
        tool_call = MagicMock(spec=ToolCall)
        tool_call.to_dict.return_value = {"mock": "tool_call"}
        tool_result = MagicMock(spec=ToolResult)
        tool_result.to_dict.return_value = {"mock": "tool_result"}

        # Add tool call history
        self.runtime_status.add_tool_calls_history(tool_call, tool_result)

        # Check if tool call history is added correctly
        self.assertEqual(len(self.runtime_status.tool_calls_history), 1)
        history_entry = self.runtime_status.tool_calls_history[0]
        self.assertEqual(history_entry["agent"], "TestAgent")
        self.assertIn("mock", history_entry["tool"])
        self.assertIn("mock", history_entry["result"])
        self.assertIsInstance(history_entry["timestamp"], str)

    def test_add_tool_error_history(self):
        tool_result = MagicMock(spec=ToolResult)
        tool_result.to_dict.return_value = {"mock": "tool_result"}

        # Add tool error history
        self.runtime_status.add_tool_error_history(tool_result)

        # Check if tool error history is added correctly
        self.assertEqual(len(self.runtime_status.tool_error_history), 1)
        error_entry = self.runtime_status.tool_error_history[0]
        self.assertEqual(error_entry["agent"], "TestAgent")
        self.assertIn("mock", error_entry["result"])
        self.assertIsInstance(error_entry["timestamp"], str)


if __name__ == '__main__':
    unittest.main()
