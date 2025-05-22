from typing import Callable


def create_tool(
        name: str,
        doc: str,
        api: Callable = None,
        args: dict = None
) -> Callable:
    # Define a local dict to store objects
    args = args if isinstance(args, dict) else {}
    local_vars = {}
    global_vars = {
        'api': api,
        'args': args,
    }

    # Define the tool in string format
    func_code = f"""
def {name}():
    if api is not None and callable(api):
        try:
            return api(**args)
        except Exception as e:
            return str(e)
    return None
"""

    # create the function by exec
    exec(func_code, global_vars, local_vars)

    # change the docstring of function
    tool = local_vars[f'{name}']
    tool.__doc__ = doc

    # return the created function
    return tool
