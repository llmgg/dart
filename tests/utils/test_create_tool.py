import unittest
from DART.utils.create_tool import create_tool


def sample_tool_api(arg1, arg2):
    return arg1 + arg2


def failing_tool_api(arg1, arg2):
    raise ValueError("This is an error")


class TestCreateTool(unittest.TestCase):

    def test_create_tool_success(self):
        # Create a tool using a sample API function
        tool = create_tool(name="test_tool", doc="This is a test tool", api=sample_tool_api,
                           args={'arg1': 1, 'arg2': 2})

        # Assert that the tool is callable
        self.assertTrue(callable(tool))

        # Assert that the tool's docstring is set correctly
        self.assertEqual(tool.__doc__, "This is a test tool")
        self.assertEqual(tool.__name__, "test_tool")

        # Assert that the tool returns the correct result
        result = tool()
        self.assertEqual(result, 3)

    def test_create_tool_no_api(self):
        # Create a tool without an API function
        tool = create_tool(name="no_api_tool", doc="This tool has no API")

        # Assert that the tool returns None when no API is provided
        result = tool()
        self.assertIsNone(result)

    def test_create_tool_with_exception(self):
        # Create a tool using an API function that raises an exception
        tool = create_tool(name="failing_tool", doc="This tool raises an exception", api=failing_tool_api,
                           args={'arg1': 1, 'arg2': 2})

        # Assert that the tool returns the exception message when an exception is raised
        result = tool()
        self.assertEqual(result, "This is an error")


if __name__ == '__main__':
    unittest.main()
