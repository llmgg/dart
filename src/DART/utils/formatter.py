import json

from .logger import logger


def to_str_format(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(e)
        try:
            return f"{obj}"
        except Exception as e:
            logger.error(e)
            return ""
