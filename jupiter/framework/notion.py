"""Framework level elements for the Notion concepts."""
import dataclasses
from dataclasses import dataclass
import typing
from typing import Optional, Generic, TypeVar

from jupiter.framework.entity import Entity
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp

NotionRowEntity = TypeVar('NotionRowEntity', bound=Entity)
NotionRowDirectExtraInfo = TypeVar('NotionRowDirectExtraInfo')
NotionRowInverseExtraInfo = TypeVar('NotionRowInverseExtraInfo')


@dataclass(frozen=True)
class BaseNotionRow:
    """A basic item type, which must contain a Notion id and an local id."""

    notion_id: NotionId
    ref_id: Optional[EntityId]
    archived: bool
    last_edited_time: Timestamp


_NotionEntitySubclass = TypeVar('_NotionEntitySubclass', bound='NotionEntity[typing.Any]')


@dataclass(frozen=True)
class NotionEntity(Generic[NotionRowEntity]):
    """Base class for Notion-side entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_row(
            entity: NotionRowEntity) \
            -> 'NotionEntity[NotionRowEntity]':
        """Construct a new Notion row from a ggiven entity."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def join_with_entity(
            self: _NotionEntitySubclass, entity: NotionRowEntity) \
            -> _NotionEntitySubclass:
        """Add to this Notion row from a given entity."""
        return typing.cast(
            _NotionEntitySubclass,
            dataclasses.replace(self.new_notion_row(entity), notion_id=self.notion_id))

    def apply_to_entity(
            self, entity: NotionRowEntity,
            modification_time: Timestamp) -> NotionRowEntity:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")


_NotionRowSubclass = TypeVar('_NotionRowSubclass', bound='NotionRow[typing.Any, typing.Any, typing.Any]')


@dataclass(frozen=True)
class NotionRow(Generic[NotionRowEntity, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo], BaseNotionRow):
    """Base class for Notion-side collection entities."""

    @staticmethod
    def new_notion_row(
            entity: NotionRowEntity, extra_info: NotionRowDirectExtraInfo) \
            -> 'NotionRow[NotionRowEntity, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def join_with_entity(
            self: _NotionRowSubclass, entity: NotionRowEntity, extra_info: NotionRowDirectExtraInfo) \
            -> _NotionRowSubclass:
        """Add to this Notion row from a given entity."""
        return typing.cast(
            _NotionRowSubclass,
            dataclasses.replace(self.new_notion_row(entity, extra_info), notion_id=self.notion_id))

    def new_entity(self, extra_info: NotionRowInverseExtraInfo) -> NotionRowEntity:
        """Construct a new entity from this notion row."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def apply_to_entity(
            self, entity: NotionRowEntity,
            extra_info: NotionRowInverseExtraInfo) -> NotionRowEntity:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")
