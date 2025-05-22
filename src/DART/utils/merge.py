import copy
from typing import List

from openai.types.chat.chat_completion_chunk import (
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)


def merge_dict(src: dict, target: dict, deepcopy: bool = False) -> dict:
    """
    Merge two dictionaries.

    :param src: Source dictionary.
    :param target: Target dictionary.
    :param deepcopy: Whether to deepcopy the target dictionary.
    :return: Merged dictionary.
    """
    if deepcopy:
        target = copy.deepcopy(target)
    if not src:
        return target

    for key, value in src.items():
        if isinstance(value, str):
            target[key] = target.get(key, None) or ''
            target[key] += value
        elif isinstance(value, list):
            target[key] = target.get(key, None) or []
            target[key] += value
        elif isinstance(value, dict):
            target[key] = target.get(key, None) or {}
            target[key] = merge_dict(value, target[key], deepcopy)
    return target


def valid_str(data):
    return data if isinstance(data, str) else ''


def merge_tool_call_function(src: ChoiceDeltaToolCallFunction, target: ChoiceDeltaToolCallFunction):
    target = target if isinstance(target, ChoiceDeltaToolCallFunction) else ChoiceDeltaToolCallFunction()

    if isinstance(src, ChoiceDeltaToolCallFunction):
        target.arguments = valid_str(target.arguments) + valid_str(src.arguments)
        target.name = valid_str(target.name) + valid_str(src.name)
    else:
        raise ValueError(f'expected ChoiceDeltaToolCallFunction, got {type(src)}')
    return target


def merge_tool_calls(src: List[ChoiceDeltaToolCall], target: List[ChoiceDeltaToolCall]):
    src_list = src if isinstance(src, List) else []
    target_list = target if isinstance(target, List) else []

    src_dict = {}
    for item in src_list:
        if isinstance(item, ChoiceDeltaToolCall):
            src_dict[item.index] = item

    target_dict = {}
    for item in target_list:
        if isinstance(item, ChoiceDeltaToolCall):
            target_dict[item.index] = item

    for key, value in src_dict.items():
        if key in target_dict:
            target_dict[key].id = valid_str(target_dict[key].id) + valid_str(value.id)
            target_dict[key].function = merge_tool_call_function(value.function, target_dict[key].function)
            target_dict[key].type = valid_str(target_dict[key].type) + valid_str(value.type)
        else:
            target_dict[key] = value

    return list(target_dict.values())
