"""A particular block of content in a note."""
import abc
from typing import Literal, cast

from jupiter.core.domain.core.url import URL
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.json import JSONDictType
from jupiter.core.framework.value import Value, value


@value
class NoteContentBlock(Value, abc.ABC):
    """A particular block of content in a note."""

    correlation_id: EntityId

    @staticmethod
    def from_json(json: JSONDictType) -> "OneOfNoteContentBlock":
        """Construct an appropriate note content block from JSON."""
        block_type = json["kind"]
        if block_type == "paragraph":
            return ParagraphBlock.from_json(json)
        elif block_type == "heading":
            return HeadingBlock.from_json(json)
        elif block_type == "bulleted-list":
            return BulletedListBlock.from_json(json)
        elif block_type == "numbered-list":
            return NumberedListBlock.from_json(json)
        elif block_type == "checklist":
            return ChecklistBlock.from_json(json)
        elif block_type == "table":
            return TableBlock.from_json(json)
        elif block_type == "code":
            return CodeBlock.from_json(json)
        elif block_type == "quote":
            return QuoteBlock.from_json(json)
        elif block_type == "divider":
            return DividerBlock.from_json(json)
        elif block_type == "link":
            return LinkBlock.from_json(json)
        elif block_type == "entity-reference":
            return EntityReferenceBlock.from_json(json)
        else:
            raise ValueError(f"Unknown note content block type: {block_type}")

    @abc.abstractmethod
    def to_json(self) -> JSONDictType:
        """Convert a note content block to JSON."""


@value
class ParagraphBlock(NoteContentBlock):
    """A paragraph of text."""

    kind: Literal["paragraph"]
    correlation_id: EntityId
    text: str

    @staticmethod
    def from_json(json: JSONDictType) -> "ParagraphBlock":
        """Create a paragraph block from JSON."""
        return ParagraphBlock(
            kind="paragraph",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a paragraph block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
        }


@value
class HeadingBlock(NoteContentBlock):
    """A heading."""

    kind: Literal["heading"]
    correlation_id: EntityId
    text: str
    level: int

    @staticmethod
    def from_json(json: JSONDictType) -> "HeadingBlock":
        """Create a heading block from JSON."""
        return HeadingBlock(
            kind="heading",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
            level=cast(int, json["level"]) if "level" in json else 1,
        )

    def to_json(self) -> JSONDictType:
        """Convert a heading block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
            "level": self.level,
        }


@value
class ListItem(Value):
    """A list item."""

    text: str
    items: list["ListItem"]

    @staticmethod
    def from_json(json: JSONDictType | str) -> "ListItem":
        """Create a list item from JSON."""
        if isinstance(json, str):
            return ListItem(
                text=json,
                items=[],
            )
        return ListItem(
            text=str(json["text"]),
            items=[
                ListItem.from_json(item)
                for item in cast(list[JSONDictType], json["items"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a list item to JSON."""
        return {
            "text": self.text,
            "items": [item.to_json() for item in self.items],
        }


@value
class BulletedListBlock(NoteContentBlock):
    """A bulleted list."""

    kind: Literal["bulleted-list"]
    correlation_id: EntityId
    items: list[ListItem]

    @staticmethod
    def from_json(json: JSONDictType) -> "BulletedListBlock":
        """Create a bulleted list block from JSON."""
        return BulletedListBlock(
            kind="bulleted-list",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=[
                ListItem.from_json(item)
                for item in cast(list[JSONDictType | str], json["items"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a bulleted list block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "items": [item.to_json() for item in self.items],
        }


@value
class NumberedListBlock(NoteContentBlock):
    """A numbered list."""

    kind: Literal["numbered-list"]
    correlation_id: EntityId
    items: list[ListItem]

    @staticmethod
    def from_json(json: JSONDictType) -> "NumberedListBlock":
        """Create a numbered list block from JSON."""
        return NumberedListBlock(
            kind="numbered-list",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=[
                ListItem.from_json(item)
                for item in cast(list[JSONDictType | str], json["items"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a numbered list block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "items": [item.to_json() for item in self.items],
        }


@value
class ChecklistItem(Value):
    """A checklist item."""

    text: str
    checked: bool

    @staticmethod
    def from_json(json: JSONDictType) -> "ChecklistItem":
        """Create a checklist item from JSON."""
        return ChecklistItem(
            text=str(json["text"]),
            checked=bool(json["checked"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a checklist item to JSON."""
        return {
            "text": self.text,
            "checked": self.checked,
        }


@value
class ChecklistBlock(NoteContentBlock):
    """A todo list."""

    kind: Literal["checklist"]
    correlation_id: EntityId
    items: list[ChecklistItem]

    @staticmethod
    def from_json(json: JSONDictType) -> "ChecklistBlock":
        """Create a checklist block from JSON."""
        return ChecklistBlock(
            kind="checklist",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=[
                ChecklistItem.from_json(item)
                for item in cast(list[JSONDictType], json["items"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a checklist block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "items": [item.to_json() for item in self.items],
        }


@value
class TableBlock(NoteContentBlock):
    """A table."""

    kind: Literal["table"]
    with_header: bool
    contents: list[list[str]]

    @staticmethod
    def from_json(json: JSONDictType) -> "TableBlock":
        """Create a table block from JSON."""
        return TableBlock(
            kind="table",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            with_header=bool(json["with_header"]),
            contents=[
                [str(cell) for cell in row]
                for row in cast(list[list[JSONDictType]], json["contents"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a table block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "with_header": self.with_header,
            "contents": self.contents,
        }


@value
class CodeBlock(NoteContentBlock):
    """A code block."""

    kind: Literal["code"]
    correlation_id: EntityId
    code: str
    language: str | None = None
    show_line_numbers: bool | None = None

    @staticmethod
    def from_json(json: JSONDictType) -> "CodeBlock":
        """Create a code block from JSON."""
        return CodeBlock(
            kind="code",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            code=str(json["code"]),
            language=str(json["language"]),
            show_line_numbers=bool(json["show_line_numbers"])
            if json["show_line_numbers"] is not None
            else None,
        )

    def to_json(self) -> JSONDictType:
        """Convert a code block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "code": self.code,
            "language": self.language,
            "show_line_numbers": self.show_line_numbers,
        }


@value
class QuoteBlock(NoteContentBlock):
    """A quote."""

    kind: Literal["quote"]
    correlation_id: EntityId
    text: str

    @staticmethod
    def from_json(json: JSONDictType) -> "QuoteBlock":
        """Create a quote block from JSON."""
        return QuoteBlock(
            kind="quote",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a quote block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
        }


@value
class DividerBlock(NoteContentBlock):
    """A divider."""

    kind: Literal["divider"]
    correlation_id: EntityId

    @staticmethod
    def from_json(json: JSONDictType) -> "DividerBlock":
        """Create a divider block from JSON."""
        return DividerBlock(
            kind="divider",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a divider block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
        }


@value
class LinkBlock(NoteContentBlock):
    """A link."""

    kind: Literal["link"]
    correlation_id: EntityId
    url: URL

    @staticmethod
    def from_json(json: JSONDictType) -> "LinkBlock":
        """Create a link block from JSON."""
        return LinkBlock(
            kind="link",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            url=URL.from_raw(cast(str, json["url"])),
        )

    def to_json(self) -> JSONDictType:
        """Convert a link block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "url": str(self.url),
        }


@value
class EntityReferenceBlock(NoteContentBlock):
    """A link."""

    kind: Literal["entity-reference"]
    correlation_id: EntityId
    entity_tag: NamedEntityTag
    ref_id: EntityId

    @staticmethod
    def from_json(json: JSONDictType) -> "EntityReferenceBlock":
        """Create an entity reference block from JSON."""
        return EntityReferenceBlock(
            kind="entity-reference",
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            entity_tag=NamedEntityTag(json["entity_tag"]),
            ref_id=EntityId.from_raw(json["ref_id"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert an entity reference block to JSON."""
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id.the_id,
            "entity_tag": str(self.entity_tag),
            "ref_id": self.ref_id.the_id,
        }


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
