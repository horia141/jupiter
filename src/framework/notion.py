"""Framework level elements for the Notion concepts."""
import dataclasses
from dataclasses import dataclass
import typing
from typing import Optional, Generic, TypeVar

from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId
from framework.base.timestamp import Timestamp

NotionRowAggregateRoot = TypeVar('NotionRowAggregateRoot', bound=AggregateRoot)
NotionRowDirectExtraInfo = TypeVar('NotionRowDirectExtraInfo')
NotionRowInverseExtraInfo = TypeVar('NotionRowInverseExtraInfo')


@dataclass(frozen=True)
class BaseNotionRow:
    """A basic item type, which must contain a Notion id and an local id."""

    notion_id: NotionId
    ref_id: Optional[str]
    archived: bool
    last_edited_time: Timestamp


_NotionEntitySubclass = TypeVar('_NotionEntitySubclass', bound='NotionEntity[typing.Any]')


@dataclass(frozen=True)
class NotionEntity(Generic[NotionRowAggregateRoot]):
    """Base class for Notion-side entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_row(
            aggregate_root: NotionRowAggregateRoot) \
            -> 'NotionEntity[NotionRowAggregateRoot]':
        """Construct a new Notion row from a ggiven aggregate root."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def join_with_aggregate_root(
            self: _NotionEntitySubclass, aggregate_root: NotionRowAggregateRoot) \
            -> _NotionEntitySubclass:
        """Add to this Notion row from a given aggregate root."""
        return typing.cast(
            _NotionEntitySubclass,
            dataclasses.replace(self.new_notion_row(aggregate_root), notion_id=self.notion_id))

    def apply_to_aggregate_root(
            self, aggregate_root: NotionRowAggregateRoot,
            modification_time: Timestamp) -> NotionRowAggregateRoot:
        """Obtain the aggregate root form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")


_NotionRowSubclass = TypeVar('_NotionRowSubclass', bound='NotionRow[typing.Any, typing.Any, typing.Any]')


@dataclass(frozen=True)
class NotionRow(Generic[NotionRowAggregateRoot, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo], BaseNotionRow):
    """Base class for Notion-side collection entities."""

    @staticmethod
    def new_notion_row(
            aggregate_root: NotionRowAggregateRoot, extra_info: NotionRowDirectExtraInfo) \
            -> 'NotionRow[NotionRowAggregateRoot, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo]':
        """Construct a new Notion row from a given aggregate root."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def join_with_aggregate_root(
            self: _NotionRowSubclass, aggregate_root: NotionRowAggregateRoot, extra_info: NotionRowDirectExtraInfo) \
            -> _NotionRowSubclass:
        """Add to this Notion row from a given aggregate root."""
        return typing.cast(
            _NotionRowSubclass,
            dataclasses.replace(self.new_notion_row(aggregate_root, extra_info), notion_id=self.notion_id))

    def new_aggregate_root(self, extra_info: NotionRowInverseExtraInfo) -> NotionRowAggregateRoot:
        """Construct a new aggregate root from this notion row."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def apply_to_aggregate_root(
            self, aggregate_root: NotionRowAggregateRoot,
            extra_info: NotionRowInverseExtraInfo) -> NotionRowAggregateRoot:
        """Obtain the aggregate root form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")
