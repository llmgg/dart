import json
import logging
import logging.config
import os
import sys
import uuid
from typing import Optional

# Define formatters for logging
FORMATTERS = {
    'verbose': {
        'format': '[%(asctime)s.%(msecs)03d :%(name)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n',
        # 'format': "[%(asctime)s.%(msecs)03d] %(message)s",
        'datefmt': "%Y-%m-%d %H:%M:%S",
    },
    'simple': {
        'format': '[%(levelname)s:%(name)s]\n%(message)s\n',
        # 'format': '[%(asctime)s.%(msecs)03d :%(name)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    },
}

# Define a base logging configuration
BASE_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': FORMATTERS,
    'handlers': {
        'sys_rotating': {
            'level': logging.DEBUG,
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10240000,
            'backupCount': 5,
            'filename': 'agent_ops.sys.log',
            'encoding': 'utf-8',
        },
        'mes_rotating': {
            'level': logging.CRITICAL,
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10240000,
            'backupCount': 10,
            'filename': 'agent_ops.mes.log',
            'encoding': 'utf-8',
        },
        'console': {
            'level': logging.INFO,
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}

# Define logging configurations for different scenarios
LOGGING_CONFIGS = {
    "file_only": {**BASE_LOGGING, 'root': {'handlers': ['sys_rotating', 'mes_rotating'], 'level': 'DEBUG'}},
    "console_only": {**BASE_LOGGING, 'root': {'handlers': ['console'], 'level': 'DEBUG'}},
    "file_console": {**BASE_LOGGING,
                     'root': {'handlers': ['console', 'sys_rotating', 'mes_rotating'], 'level': 'DEBUG'}},
    "none": {'version': 1, 'disable_existing_loggers': True},
}


def setup_main_logger(file=True, console=True, path: Optional[str] = None):
    """
    Configures logging for the main application.
    Allows separate configurations for file and console logging.
    """
    # Check environment variable to disable file logging
    disable_file_logging = os.getenv('DART_LOG_FILE', '').lower() in ('false', '0', 'no')

    if disable_file_logging:
        file = False

    config_name = "none"
    if file and console:
        config_name = "file_console"
    elif file:
        config_name = "file_only"
    elif console:
        config_name = "console_only"

    log_config = LOGGING_CONFIGS[config_name]

    if path and file:
        expanded_path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
        log_config["handlers"]["sys_rotating"]["filename"] = f"{expanded_path}.sys.log"
        log_config["handlers"]["mes_rotating"]["filename"] = f"{expanded_path}.mes.log"

    logging.config.dictConfig(log_config)

    def exception_hook(exc_type, exc_value, exc_traceback):
        logging.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = exception_hook

    return logging.getLogger("chatbot")


LoggerPath = '~/'
logger = setup_main_logger(path=LoggerPath + '.dart')


def str_format(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(e)
        try:
            return f"{obj}"
        except Exception as e:
            logger.error(e)
            return ""


class Tracer:
    def __init__(self, path='~/.tracer/record', tracer_id: str | None = None):
        tracer_id = tracer_id or uuid.uuid4().hex
        self.path = '_'.join([path, tracer_id])
        directory = os.path.dirname(self.path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.logger = setup_main_logger(path=self.path)

    def record(self, obj, formatted=True):
        if formatted:
            self.logger.info(str_format(obj))
        else:
            self.logger.info(obj)
