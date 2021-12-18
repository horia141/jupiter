"""Common types for Notion."""
from dataclasses import dataclass
from typing import NewType, List, Optional

from domain.entity_name import EntityName
from models.framework import NotionId

NotionLockKey = NewType("NotionLockKey", str)


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
class NotionPageLinkExtra:
    """A descriptor for a Notion page like in Windows."""
    page_id: NotionId
    name: str


@dataclass()
class NotionCollectionLink:
    """A descriptor for a Notion collection page."""
    page_id: NotionId
    collection_id: NotionId


@dataclass()
class NotionCollectionLinkExtra:
    """Glad we're going down the route of Windows."""
    page_id: NotionId
    collection_id: NotionId
    name: str


def format_name_for_option(option_name: EntityName) -> str:
    """Nicely format the name of an option."""
    output = ""
    last_char = None
    for char in str(option_name):
        if char.isalnum() or (char == " " and last_char != " "):
            output += char
            last_char = char
    return output


def clean_eisenhower(raw_eisen: Optional[List[str]]) -> List[str]:
    """Clean the raw Eisenhower values from Notion."""
    if raw_eisen is None:
        return []
    return [e for e in raw_eisen if e != '']
