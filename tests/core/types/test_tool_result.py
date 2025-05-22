import unittest

from DART.core.base.agent import Agent
from DART.core.types.tool_result import ToolResult, ToolResultType


class TestToolResult(unittest.TestCase):

    def test_tool_result_initialization_string(self):
        result = ToolResult(name="TestTool", description="A test tool", result_value="some string",
                            result_type=ToolResultType.STRING.value)
        self.assertEqual(result.name, "TestTool")
        self.assertEqual(result.description, "A test tool")
        self.assertEqual(result.result_value, "some string")
        self.assertEqual(result.result_type, ToolResultType.STRING.value)

    def test_tool_result_initialization_agent(self):
        agent = Agent(name='agent', persona='a test agent', description='the description of the agent')
        result = ToolResult(name="TestTool", description="A test tool", result_value=agent,
                            result_type=ToolResultType.AGENT.value)
        self.assertEqual(result.result_value, agent)
        self.assertEqual(result.result_type, ToolResultType.AGENT.value)

    def test_tool_result_initialization_none(self):
        result = ToolResult(name="TestTool", description="A test tool", result_value=None,
                            result_type=ToolResultType.NONE.value)
        self.assertIsNone(result.result_value)
        self.assertEqual(result.result_type, ToolResultType.NONE.value)

    def test_invalid_result_type(self):
        with self.assertRaises(ValueError):
            ToolResult(name="TestTool", description="A test tool", result_value="invalid", result_type="invalid_type")

    def test_invalid_result_value_for_string(self):
        with self.assertRaises(ValueError):
            ToolResult(name="TestTool", description="A test tool", result_value=123,
                       result_type=ToolResultType.STRING.value)

    def test_invalid_result_value_for_agent(self):
        with self.assertRaises(ValueError):
            ToolResult(name="TestTool", description="A test tool", result_value="not an agent",
                       result_type=ToolResultType.AGENT.value)

    def test_invalid_result_value_for_none(self):
        with self.assertRaises(ValueError):
            ToolResult(name="TestTool", description="A test tool", result_value="should be none",
                       result_type=ToolResultType.NONE.value)


if __name__ == '__main__':
    unittest.main()
