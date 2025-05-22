import unittest
from unittest.mock import Mock
from typing import List
import json

from DART.core.base.agent import Agent
from DART.core.types.choice import ToolCall, ToolCallFunction
from DART.core.types.tool_result import ToolResult, ToolResultType
from DART.utils.create_tool import create_tool


class TestAgent(unittest.TestCase):

    def setUp(self):
        # 创建一个简单的 mock 函数来模拟工具
        def mock_tool(arg1, arg2):
            """test doc for tool"""
            return str(arg1) + str(arg2)

        self.mock_tool = mock_tool

        # 创建一个简单的 mock Agent
        self.mock_agent = Agent(
            name="MockAgent",
            persona="A mock agent persona",
            description="A mock agent description"
        )

    def test_agent_initialization(self):
        # 测试 Agent 的初始化
        agent = Agent(
            name="TestAgent",
            persona="Test persona",
            description="Test description",
            tools=[self.mock_tool],
            handoffs=[self.mock_agent]
        )
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.persona, "Test persona")
        self.assertEqual(agent.description, "Test description")
        self.assertIn(self.mock_tool, agent.__tools__)
        self.assertIn(self.mock_agent, agent.__handoffs__)

    def test_transfer_handoffs_to_tools(self):
        # 测试 __handoffs__ 转换为工具
        agent = Agent(
            name="TestAgent",
            persona="Test persona",
            description="Test description",
            handoffs=[self.mock_agent]
        )
        tools = agent.transfer_handoffs_to_tools()
        self.assertEqual(len(tools), 1)
        self.assertTrue(callable(tools[0]))
        self.assertEqual(self.mock_agent.name, tools[0].__name__)
        self.assertIn(self.mock_agent.persona, tools[0].__doc__)
        self.assertIn(self.mock_agent.description, tools[0].__doc__)
        self.assertTrue(isinstance(tools[0](), Agent))
        self.assertEqual(tools[0](), self.mock_agent)

    def test_run_tools(self):
        # 测试工具的运行
        agent = Agent(
            name="TestAgent",
            persona="Test persona",
            description="Test description",
            tools=[self.mock_tool]
        )

        # 创建 ToolCall 的模拟实例
        tool_call = ToolCall(
            function=ToolCallFunction(
                name='mock_tool',
                arguments=json.dumps({"arg1": 'test1', "arg2": 'test2'}),
            )
        )

        results = agent.run_tools([tool_call])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, self.mock_tool.__name__)
        self.assertEqual(results[0].description, self.mock_tool.__doc__)
        self.assertEqual(results[0].result_value, 'test1test2')
        self.assertEqual(results[0].result_type, ToolResultType.STRING.value)

    def test_run_tools_with_exception(self):
        # 测试工具运行时的异常处理
        def failing_tool(arg1, arg2):
            raise ValueError("This is an error info for failing_tool")

        agent = Agent(
            name="TestAgent",
            persona="Test persona",
            description="Test description",
            tools=[failing_tool]
        )

        tool_call = ToolCall(
            function=ToolCallFunction(
                name='failing_tool',
                arguments=json.dumps({"arg1": 1, "arg2": 2}),
            )
        )

        results = agent.run_tools([tool_call])
        self.assertEqual(len(results), 1)
        self.assertIn("Error while calling tool", results[0].result_value)
        self.assertIn("This is an error info for failing_tool", results[0].result_value)
        self.assertEqual(results[0].result_type, ToolResultType.STRING.value)

    def test_transfer_agent_to_tool(self):
        # 测试将 Agent 转换为工具
        agent = Agent(
            name="TestAgent",
            persona="Test persona",
            description="Test description",
        )
        tool = agent.to_tool()
        self.assertTrue(callable(tool))
        self.assertEqual(tool.__name__, agent.name)
        self.assertIn('这是一个Agent实例，该Agent对应的角色和具体功能如下', tool.__doc__)

        tool_result = tool()
        self.assertTrue(isinstance(tool_result, Agent))
        self.assertEqual(tool_result.name, agent.name)
        self.assertEqual(tool_result.persona, agent.persona)
        self.assertEqual(tool_result.description, agent.description)


if __name__ == '__main__':
    unittest.main()
