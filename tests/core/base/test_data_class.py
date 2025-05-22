import json
import unittest

from DART.core.base.data_class import valid_str, valid_list, valid_dict, DataClass, dict_to_dataclass
from DART.utils.formatter import to_str_format


class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.data = DataClass()
        self.data.set('name', 'test')
        self.data.set('value', 100)
        self.data.set('none_field', None)

    def test_to_dict(self):
        result = self.data.to_dict(include_none=False)
        self.assertEqual(result, {'name': 'test', 'value': 100})

        result_include_none = self.data.to_dict(include_none=True)
        self.assertEqual(result_include_none, {'name': 'test', 'value': 100, 'none_field': None})

    def test_to_string(self):
        expected_string = to_str_format({'name': 'test', 'value': 100})
        self.assertEqual(self.data.to_string(include_none=False), expected_string)

    def test_to_json(self):
        expected_json = json.loads(to_str_format({'name': 'test', 'value': 100}))
        self.assertEqual(self.data.to_json(include_none=False), expected_json)

    def test_keys(self):
        keys = self.data.keys(include_none=False)
        self.assertEqual(set(keys), {'name', 'value'})

        keys_include_none = self.data.keys(include_none=True)
        self.assertEqual(set(keys_include_none), {'name', 'value', 'none_field'})

    def test_set_and_get(self):
        self.data.set('new_key', 'new_value')
        self.assertEqual(self.data.get('new_key'), 'new_value')
        self.assertEqual(self.data.get('non_existent_key', 'default'), 'default')

    def test_has(self):
        self.assertTrue(self.data.has('name'))
        self.assertFalse(self.data.has('non_existent_key'))

    def test_update(self):
        other = DataClass()
        other.set('name', 'updated')
        other.set('new_field', 'new_value')

        self.data.update(other)
        self.assertEqual(self.data.get('name'), 'updated')
        self.assertEqual(self.data.get('new_field'), 'new_value')

    def test_content_is_empty(self):
        data = DataClass()
        data.set('name', 'test')
        data.set('value', 100)
        data.set('none_field', None)
        self.assertFalse(data.content_is_none(['name']))
        self.assertFalse(data.content_is_none(['name', 'none_field']))
        self.assertFalse(data.content_is_none(['value', 'none_field']))
        self.assertTrue(data.content_is_none(['none_field']))
        self.assertTrue(data.content_is_none(['non_existent_key']))

    def test_valid_str(self):
        self.assertEqual(valid_str("hello"), "hello")
        self.assertEqual(valid_str(123), "")
        self.assertEqual(valid_str(None), "")

    def test_valid_list(self):
        self.assertEqual(valid_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(valid_list("not a list"), [])
        self.assertEqual(valid_list(None), [])

    def test_valid_dict(self):
        self.assertEqual(valid_dict({"key": "value"}), {"key": "value"})
        self.assertEqual(valid_dict("not a dict"), {})
        self.assertEqual(valid_dict(None), {})

    def test_data_class_to_dict(self):
        dc = DataClass()
        dc.set('key1', 'value1')
        dc.set('key2', None)
        self.assertEqual(dc.to_dict(include_none=True), {'key1': 'value1', 'key2': None})
        self.assertEqual(dc.to_dict(include_none=False), {'key1': 'value1'})

    def test_data_class_update(self):
        dc1 = DataClass()
        dc1.set('key1', 'value1')

        dc2 = DataClass()
        dc2.set('key1', 'new_value')
        dc2.set('key2', 'value2')

        dc1.update(dc2)
        self.assertEqual(dc1.to_dict(), {'key1': 'new_value', 'key2': 'value2'})

    def test_dict_to_dataclass(self):
        input_dict = {'key1': 'value1', 'key2': {'nested_key': 'nested_value'}}
        dc = dict_to_dataclass(input_dict)
        self.assertEqual(dc.get('key1'), 'value1')
        self.assertTrue(isinstance(dc.get('key2'), DataClass))
        self.assertEqual(dc.get('key2').get('nested_key'), 'nested_value')


if __name__ == '__main__':
    unittest.main()
