"""Common types for Notion."""
from dataclasses import dataclass
from typing import NewType, List, Optional


NotionLockKey = NewType("NotionLockKey", str)
NotionId = NewType("NotionId", str)


class PageError(Exception):
    """Exception for Notion pages interaction."""


class PageNotFoundError(PageError):
    """Exception raised when a page wasn't found."""


class CollectionError(Exception):
    """Exception for Notion interactions."""


class CollectionEntityAlreadyExists(CollectionError):
    """Exception for when a particular entity already exists but should not."""


class CollectionEntityNotFound(CollectionError):
    """Exception for when a particular entity is not found."""


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
