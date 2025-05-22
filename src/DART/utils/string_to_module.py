import importlib
import os
import uuid

from .logger import logger


class StringToModule:
    def __init__(self, code: str, doc: str = ''):
        self.code = code if code else ''
        self.doc = doc

    def getattr(self, name, default=None):
        module_name = 'python_module_' + uuid.uuid4().hex
        file_name = module_name + '.py'
        with open(file_name, 'w') as file:
            file.write(self.code)

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logger.info(e)
            module = None

        if os.path.exists(file_name):
            os.remove(file_name)

        if module:
            func = getattr(module, name, default)
            if callable(func):
                func.__doc__ = self.doc
            return func
        else:
            return default
