"""A particular block of content in a note."""
from dataclasses import dataclass

from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.value import Value


@dataclass
class NoteContentBlock(Value):
    """A particular block of content in a note."""

    correlation_id: EntityId


@dataclass
class ParagraphBlock(NoteContentBlock):
    """A paragraph of text."""

    text: str


@dataclass
class HeadingBlock(NoteContentBlock):
    """A heading."""

    text: str


@dataclass
class BulletedListBlock(NoteContentBlock):
    """A bulleted list."""

    items: list[str]


@dataclass
class NumberedListBlock(NoteContentBlock):
    """A numbered list."""

    items: list[str]


@dataclass
class ChecklistItem(Value):
    """A checklist item."""

    text: str
    checked: bool


@dataclass
class ChecklistBlock(NoteContentBlock):
    """A todo list."""

    items: list[ChecklistItem]


@dataclass
class QuoteBlock(NoteContentBlock):
    """A quote."""

    text: str


@dataclass
class DividerBlock(NoteContentBlock):
    """A divider."""


@dataclass
class LinkBlock(NoteContentBlock):
    """A link."""

    url: URL


@dataclass
class EntityReferenceBlock(NoteContentBlock):
    """A link."""

    entity_tag: NamedEntityTag
    ref_id: EntityId
