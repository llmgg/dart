import json
from dataclasses import dataclass
from typing import Dict, Any, List, Type

from ...utils.formatter import to_str_format


def valid_value(value: Any, data_type: Type) -> Any:
    return value if isinstance(value, data_type) else data_type()


def valid_str(value: Any) -> str:
    return valid_value(value, str)


def valid_list(value: Any) -> List:
    return valid_value(value, list)


def valid_dict(value: Any) -> Dict:
    return valid_value(value, dict)


def valid_dataclass(value: Any) -> 'DataClass':
    return valid_value(value, DataClass)


simple_types = (str, float, int, bool)


def unwrap_list(value: list) -> list:
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(unwrap_dict(item))
        elif isinstance(item, list):
            result.append(unwrap_list(item))
        elif isinstance(item, DataClass):
            result.append(item.to_dict(include_none=True))
        else:
            result.append(item)
    return result


def unwrap_dict(value: dict) -> dict:
    result = {}
    for key, value in value.items():
        if isinstance(value, dict):
            result[key] = unwrap_dict(value)
        elif isinstance(value, list):
            result[key] = unwrap_list(value)
        elif isinstance(value, DataClass):
            result[key] = value.to_dict(include_none=True)
        else:
            result[key] = value
    return result


@dataclass
class DataClass:
    # id: str = None
    #
    # def __init__(self):
    #     self.id = uuid.uuid4().hex
    #
    # def __hash__(self):
    #     return hash(self.id)
    #
    # def __eq__(self, other):
    #     if isinstance(other, DataClass):
    #         return self.id == other.id
    #     return False

    def to_dict(self, include_none: bool = True) -> Dict:
        if include_none:
            attrs = {key: value for key, value in self.__dict__.items()}
        else:
            attrs = {
                key: value for key, value in self.__dict__.items() if value is not None
            }
        result = {}
        for key, value in attrs.items():
            if isinstance(value, DataClass):
                result[key] = value.to_dict(include_none=include_none)
            elif isinstance(value, dict):
                result[key] = unwrap_dict(value)
            elif isinstance(value, list):
                result[key] = unwrap_list(value)
            else:
                result[key] = value
        return result

    def to_string(self, include_none: bool = True) -> str:
        return to_str_format(self.to_dict(include_none=include_none))

    def to_json(self, include_none: bool = True) -> str:
        return json.loads(self.to_string(include_none=include_none))

    def keys(self, include_none: bool = True) -> List:
        if include_none:
            return [key for key, value in self.__dict__.items()]
        return [key for key, value in self.__dict__.items() if value is not None]

    def set(self, key: str, value: Any, include_none: bool = True):
        if include_none:
            setattr(self, key, value)
        else:
            if value is not None:
                setattr(self, key, value)

    def get(self, key: str, default: Any | None = None, include_none: bool = True):
        value = getattr(self, key, default)
        if include_none:
            return value
        return value or default

    def has(self, key: str, include_none: bool = True) -> bool:
        return key in self.keys(include_none=include_none)

    def update(self, other: 'DataClass', include_none: bool = False):
        for key, value in other.__dict__.items():
            if value is None:
                if include_none:
                    setattr(self, key, value)
            elif isinstance(value, (dict, DataClass)):
                if isinstance(value, dict):
                    value = dict_to_dataclass(value, include_none=include_none)
                current_value = valid_dataclass(getattr(self, key, None))
                current_value.update(value, include_none=include_none)
                setattr(self, key, current_value)
            else:
                setattr(self, key, value)

    def __merge(self, other: 'DataClass'):
        for key, value in other.__dict__.items():
            if value is None:
                continue
            elif isinstance(value, (dict, DataClass)):
                if isinstance(value, dict):
                    value = dict_to_dataclass(value, include_none=False)
                current_value = valid_dataclass(getattr(self, key, None))
                current_value.__merge(value)
                setattr(self, key, current_value)
            elif isinstance(value, str):
                setattr(self, key, valid_str(getattr(self, key, '')) + value)
            elif isinstance(value, list):
                setattr(self, key, valid_list(getattr(self, key, [])) + value)
            else:
                setattr(self, key, value)

    def is_empty(self) -> bool:
        ...

    def content_is_none(self, content_keys: List[str]) -> bool:
        content_keys = valid_list(content_keys)
        return not bool(set(content_keys) & set(self.keys(include_none=False)))

    def clone(self, include_none: bool = True) -> 'DataClass':
        return dict_to_dataclass(self.to_dict(include_none=include_none), include_none=include_none)

    def __str__(self):
        return self.to_string(include_none=True)


def list_to_dataclass(input_list: List) -> List[DataClass]:
    result = []
    for item in input_list:
        if isinstance(item, dict):
            result.append(dict_to_dataclass(item, include_none=True))
        elif isinstance(item, list):
            result.append(list_to_dataclass(item))
        else:
            result.append(item)
    return result


def dict_to_dataclass(input_dict: dict, include_none: bool = True) -> DataClass:
    dc_result = DataClass()
    for key, value in input_dict.items():
        if value is None:
            if include_none:
                dc_result.set(key, value)
        elif isinstance(value, dict):
            dc_result.set(key, dict_to_dataclass(value, include_none=include_none))
        elif isinstance(value, list):
            dc_result.set(key, list_to_dataclass(value))
        else:
            dc_result.set(key, value)
    return dc_result
