import unittest

from DART.core.types.dataset import DataSet
from DART.core.types.dataset import DataSetType


class TestDataSet(unittest.TestCase):

    def test_default_values(self):
        dataset = DataSet()
        self.assertEqual(dataset.name, None)
        self.assertEqual(dataset.title, None)
        self.assertEqual(dataset.labels, None)
        self.assertIsNone(dataset.meta_data)
        self.assertEqual(dataset.src_set, None)
        self.assertEqual(dataset.dest_set, None)
        self.assertEqual(dataset.dataset_type, DataSetType.NODE.value)

    def test_custom_values(self):
        dataset = DataSet(
            name='MyDataset',
            title='This is a test dataset',
            labels=['label1', 'label2'],
            meta_data={'key': 'value'},
            src_set=[DataSet(name='src1'), DataSet(name='src2')],
            dest_set=[DataSet(name='dest1'), DataSet(name='dest2')],
            dataset_type=DataSetType.EDGE.value,
            custom_arg='custom_value'
        )
        self.assertEqual(dataset.name, 'MyDataset')
        self.assertEqual(dataset.title, 'This is a test dataset')
        self.assertEqual(dataset.labels, ['label1', 'label2'])
        self.assertEqual(dataset.meta_data, {'key': 'value'})
        self.assertEqual(len(dataset.src_set), 2)
        self.assertEqual(len(dataset.dest_set), 2)
        self.assertEqual(dataset.dataset_type, DataSetType.EDGE.value)
        self.assertEqual(dataset.kwargs, {'custom_arg': 'custom_value'})

    def test_is_empty_method(self):
        dataset = DataSet()
        self.assertTrue(dataset.is_empty())

        dataset = DataSet(meta_data={'key': 'value'})
        self.assertFalse(dataset.is_empty())

    def test_invalid_dataset_type(self):
        with self.assertRaises(ValueError):
            DataSet(dataset_type='invalid_type')

    def test_valid_dataset_type(self):
        dataset = DataSet(dataset_type=DataSetType.NODE.value)
        self.assertEqual(dataset.dataset_type, DataSetType.NODE.value)

        dataset = DataSet(dataset_type=DataSetType.EDGE.value)
        self.assertEqual(dataset.dataset_type, DataSetType.EDGE.value)


if __name__ == '__main__':
    unittest.main()
