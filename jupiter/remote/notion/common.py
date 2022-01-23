"""Common types for Notion."""
from typing import NewType

from jupiter.domain.entity_name import EntityName

NotionLockKey = NewType("NotionLockKey", str)


def format_name_for_option(option_name: EntityName) -> str:
    """Nicely format the name of an option."""
    output = ""
    last_char = None
    for char in str(option_name):
        if char.isalnum() or (char == " " and last_char != " "):
            output += char
            last_char = char
    return output
