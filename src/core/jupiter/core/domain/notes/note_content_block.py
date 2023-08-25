"""A particular block of content in a note."""
import abc
from dataclasses import dataclass
from typing import cast

from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.json import JSONDictType
from jupiter.core.framework.value import Value


@dataclass
class NoteContentBlock(Value, abc.ABC):
    """A particular block of content in a note."""

    correlation_id: EntityId

    @staticmethod
    def from_json(json: JSONDictType) -> "NoteContentBlock":
        """Construct an appropriate note content block from JSON."""
        block_type = json["type"]
        if block_type == ParagraphBlock.__name__:
            return ParagraphBlock.from_json(json)
        elif block_type == HeadingBlock.__name__:
            return HeadingBlock.from_json(json)
        elif block_type == BulletedListBlock.__name__:
            return BulletedListBlock.from_json(json)
        elif block_type == NumberedListBlock.__name__:
            return NumberedListBlock.from_json(json)
        elif block_type == ChecklistBlock.__name__:
            return ChecklistBlock.from_json(json)
        elif block_type == QuoteBlock.__name__:
            return QuoteBlock.from_json(json)
        elif block_type == DividerBlock.__name__:
            return DividerBlock.from_json(json)
        elif block_type == LinkBlock.__name__:
            return LinkBlock.from_json(json)
        elif block_type == EntityReferenceBlock.__name__:
            return EntityReferenceBlock.from_json(json)
        else:
            raise ValueError(f"Unknown note content block type: {block_type}")

    @abc.abstractmethod
    def to_json(self) -> JSONDictType:
        """Convert a note content block to JSON."""


@dataclass
class ParagraphBlock(NoteContentBlock):
    """A paragraph of text."""

    text: str

    @staticmethod
    def from_json(json: JSONDictType) -> "ParagraphBlock":
        """Create a paragraph block from JSON."""
        return ParagraphBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a paragraph block to JSON."""
        return {
            "type": ParagraphBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
        }


@dataclass
class HeadingBlock(NoteContentBlock):
    """A heading."""

    text: str

    @staticmethod
    def from_json(json: JSONDictType) -> "HeadingBlock":
        """Create a heading block from JSON."""
        return HeadingBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a heading block to JSON."""
        return {
            "type": HeadingBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
        }


@dataclass
class BulletedListBlock(NoteContentBlock):
    """A bulleted list."""

    items: list[str]

    @staticmethod
    def from_json(json: JSONDictType) -> "BulletedListBlock":
        """Create a bulleted list block from JSON."""
        return BulletedListBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=cast(list[str], json["items"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a bulleted list block to JSON."""
        return {
            "type": BulletedListBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "items": self.items,
        }


@dataclass
class NumberedListBlock(NoteContentBlock):
    """A numbered list."""

    items: list[str]

    @staticmethod
    def from_json(json: JSONDictType) -> "NumberedListBlock":
        """Create a numbered list block from JSON."""
        return NumberedListBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=cast(list[str], json["items"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a numbered list block to JSON."""
        return {
            "type": NumberedListBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "items": self.items,
        }


@dataclass
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


@dataclass
class ChecklistBlock(NoteContentBlock):
    """A todo list."""

    items: list[ChecklistItem]

    @staticmethod
    def from_json(json: JSONDictType) -> "ChecklistBlock":
        """Create a checklist block from JSON."""
        return ChecklistBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            items=[
                ChecklistItem.from_json(item)
                for item in cast(list[JSONDictType], json["items"])
            ],
        )

    def to_json(self) -> JSONDictType:
        """Convert a checklist block to JSON."""
        return {
            "type": ChecklistBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "items": [item.to_json() for item in self.items],
        }


@dataclass
class QuoteBlock(NoteContentBlock):
    """A quote."""

    text: str

    @staticmethod
    def from_json(json: JSONDictType) -> "QuoteBlock":
        """Create a quote block from JSON."""
        return QuoteBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            text=str(json["text"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a quote block to JSON."""
        return {
            "type": QuoteBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "text": self.text,
        }


@dataclass
class DividerBlock(NoteContentBlock):
    """A divider."""

    @staticmethod
    def from_json(json: JSONDictType) -> "DividerBlock":
        """Create a divider block from JSON."""
        return DividerBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert a divider block to JSON."""
        return {
            "type": DividerBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
        }


@dataclass
class LinkBlock(NoteContentBlock):
    """A link."""

    url: URL

    @staticmethod
    def from_json(json: JSONDictType) -> "LinkBlock":
        """Create a link block from JSON."""
        return LinkBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            url=URL.from_raw(cast(str, json["url"])),
        )

    def to_json(self) -> JSONDictType:
        """Convert a link block to JSON."""
        return {
            "type": LinkBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "url": str(self.url),
        }


@dataclass
class EntityReferenceBlock(NoteContentBlock):
    """A link."""

    entity_tag: NamedEntityTag
    ref_id: EntityId

    @staticmethod
    def from_json(json: JSONDictType) -> "EntityReferenceBlock":
        """Create an entity reference block from JSON."""
        return EntityReferenceBlock(
            correlation_id=EntityId.from_raw(json["correlation_id"]),
            entity_tag=NamedEntityTag(json["entity_tag"]),
            ref_id=EntityId.from_raw(json["ref_id"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert an entity reference block to JSON."""
        return {
            "type": EntityReferenceBlock.__name__,
            "correlation_id": self.correlation_id.the_id,
            "entity_tag": str(self.entity_tag),
            "ref_id": self.ref_id.the_id,
        }
