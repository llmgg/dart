import enum
from typing import List, Any

from ..base.data_class import DataClass, valid_dict


class DataSetType(enum.Enum):
    NODE = 'node'
    EDGE = 'edge'


class DataSet(DataClass):
    def __init__(
            self,
            name: str | None = None,
            title: str | None = None,
            labels: List[str] | None = None,
            meta_data: Any | None = None,
            src_set: List['DataSet'] | None = None,
            dest_set: List['DataSet'] | None = None,
            dataset_type: str | None = None,
            **kwargs
    ):
        super().__init__()
        """Unique identifier for the dataset."""
        self.name = name

        """Short description of the dataset."""
        self.title = title

        """Labels associated with the dataset."""
        self.labels = labels

        """The meta data associated with the dataset."""
        self.meta_data = meta_data

        """The source and destination datasets of the dataset."""
        self.src_set = src_set
        self.dest_set = dest_set

        """The type of the dataset, it should be either 'node' or 'edge'."""
        if dataset_type not in [None, DataSetType.NODE.value, DataSetType.EDGE.value]:
            raise ValueError("dataset_type must be either 'node' or 'edge'")
        self.dataset_type = dataset_type or DataSetType.NODE.value
        self.kwargs = valid_dict(kwargs)

    def is_empty(self):
        return not self.meta_data
