"""Common types for Notion."""
from dataclasses import dataclass
from typing import NewType, List, Optional

NotionId = NewType("NotionId", str)


class CollectionError(Exception):
    """Exception for Notion interactions."""


@dataclass()
class NotionPageLink:
    """A descriptor for a Notion page."""
    page_id: NotionId


@dataclass()
class NotionCollectionLink:
    """A descriptor for a Notion collection page."""
    page_id: NotionId
    collection_id: NotionId


def format_name_for_option(option_name: str) -> str:
    """Nicely format the name of an option."""
    output = ""
    last_char = None
    for char in option_name:
        if char.isalnum() or (char == " " and last_char != " "):
            output += char
            last_char = char
    return output


def clean_eisenhower(raw_eisen: Optional[List[str]]) -> List[str]:
    """Clean the raw Eisenhower values from Notion."""
    if raw_eisen is None:
        return []
    return [e for e in raw_eisen if e != '']
