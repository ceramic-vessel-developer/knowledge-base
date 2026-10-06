from enum import Enum


class MessageAuthor(str, Enum):
    USER = "user"
    AI = "ai"
