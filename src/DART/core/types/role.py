import enum


class Role(enum.Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'
    TOOL = 'tool'

    @classmethod
    def values(cls):
        return [role.value for role in cls]
