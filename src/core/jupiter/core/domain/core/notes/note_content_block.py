"""A particular block of content in a note."""
import abc
from typing import Literal

from jupiter.core.domain.core.url import URL
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId, EntityIdDatabaseDecoder
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import RealmDecodingError
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    hashable_value,
    value,
)

_ENTITY_ID_DECODER = EntityIdDatabaseDecoder()


@hashable_value
class CorrelationId(AtomicValue):
    """A generic entity id."""

    the_id: str

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "CorrelationId":
        """Validate and clean an correlation id."""
        if not isinstance(value, str):
            raise InputValidationError("Expected correlation id to be string")

        return CorrelationId(CorrelationId._clean_the_id(value))

    def to_primitive(self) -> Primitive:
        return self.the_id

    @staticmethod
    def _clean_the_id(correlation_id_raw: str) -> str:
        correlation_id: str = correlation_id_raw.strip()

        if len(correlation_id) == 0:
            raise RealmDecodingError("Expected correlation id to be non-empty")

        return correlation_id


@value
class NoteContentBlock(CompositeValue, abc.ABC):
    """A particular block of content in a note."""

    correlation_id: CorrelationId


@value
class ParagraphBlock(NoteContentBlock):
    """A paragraph of text."""

    kind: Literal["paragraph"]
    correlation_id: CorrelationId
    text: str


@value
class HeadingBlock(NoteContentBlock):
    """A heading."""

    kind: Literal["heading"]
    correlation_id: CorrelationId
    text: str
    level: int


@value
class ListItem(CompositeValue):
    """A list item."""

    text: str
    items: list["ListItem"]


@value
class BulletedListBlock(NoteContentBlock):
    """A bulleted list."""

    kind: Literal["bulleted-list"]
    correlation_id: CorrelationId
    items: list[ListItem]


@value
class NumberedListBlock(NoteContentBlock):
    """A numbered list."""

    kind: Literal["numbered-list"]
    correlation_id: CorrelationId
    items: list[ListItem]


@value
class ChecklistItem(CompositeValue):
    """A checklist item."""

    text: str
    checked: bool


@value
class ChecklistBlock(NoteContentBlock):
    """A todo list."""

    kind: Literal["checklist"]
    correlation_id: CorrelationId
    items: list[ChecklistItem]


@value
class TableBlock(NoteContentBlock):
    """A table."""

    kind: Literal["table"]
    with_header: bool
    contents: list[list[str]]


@value
class CodeBlock(NoteContentBlock):
    """A code block."""

    kind: Literal["code"]
    correlation_id: CorrelationId
    code: str
    language: str | None = None
    show_line_numbers: bool | None = None


@value
class QuoteBlock(NoteContentBlock):
    """A quote."""

    kind: Literal["quote"]
    correlation_id: CorrelationId
    text: str


@value
class DividerBlock(NoteContentBlock):
    """A divider."""

    kind: Literal["divider"]
    correlation_id: CorrelationId


@value
class LinkBlock(NoteContentBlock):
    """A link."""

    kind: Literal["link"]
    correlation_id: CorrelationId
    url: URL


@value
class EntityReferenceBlock(NoteContentBlock):
    """A link."""

    kind: Literal["entity-reference"]
    correlation_id: CorrelationId
    entity_tag: NamedEntityTag
    ref_id: EntityId


OneOfNoteContentBlock = (
    ParagraphBlock
    | HeadingBlock
    | BulletedListBlock
    | NumberedListBlock
    | ChecklistBlock
    | TableBlock
    | CodeBlock
    | QuoteBlock
    | DividerBlock
    | LinkBlock
    | EntityReferenceBlock
)
