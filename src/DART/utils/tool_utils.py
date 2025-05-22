import inspect
import random
import uuid
from typing import Callable


def create_tool_desc(func: Callable, index: int = None, id: str = None) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        None: "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f'''Failed to get signature for tool "{func.__name__}": {str(e)}'''
        )

    parameters = {}
    required = []
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f'''Unknown type annotation "{param.annotation}" for parameter "{param.name}": {str(e)}'''
            )
        if param.default is inspect.Parameter.empty:
            parameters[param.name] = {
                "type": param_type,
                "description": '',
            }
            required.append(param.name)
        else:
            parameters[param.name] = {
                "type": param_type,
                "description": '',
                "default": param.default,
            }

    return {
        "index": index or random.randint(0, 1024000),
        "id": id or uuid.uuid4().hex,
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
        "type": "function",
    }
