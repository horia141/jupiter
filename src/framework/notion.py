"""Framework level elements for the Notion concepts."""
from dataclasses import dataclass
from typing import Optional, Generic, NewType, TypeVar

from framework.base.timestamp import Timestamp
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId

NotionRowAggregateRoot = TypeVar('NotionRowAggregateRoot', bound=AggregateRoot)
NotionRowDirectExtraInfo = TypeVar('NotionRowDirectExtraInfo')
NotionRowInverseExtraInfo = TypeVar('NotionRowInverseExtraInfo')


NotionId = NewType("NotionId", str)
BAD_NOTION_ID = NotionId("bad-notion-id")


@dataclass(frozen=True)
class BaseNotionRow:
    """A basic item type, which must contain a Notion id and an local id."""

    notion_id: NotionId
    ref_id: Optional[str]


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
            self, aggregate_root: NotionRowAggregateRoot) \
            -> 'NotionEntity[NotionRowAggregateRoot]':
        """Add to this Notion row from a given aggregate root."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def apply_to_aggregate_root(
            self, aggregate_root: NotionRowAggregateRoot,
            modification_time: Timestamp) -> NotionRowAggregateRoot:
        """Obtain the aggregate root form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")


@dataclass(frozen=True)
class NotionRow(Generic[NotionRowAggregateRoot, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo], BaseNotionRow):
    """Base class for Notion-side collection entities."""

    last_edited_time: Timestamp

    @staticmethod
    def new_notion_row(
            aggregate_root: NotionRowAggregateRoot, extra_info: NotionRowDirectExtraInfo) \
            -> 'NotionRow[NotionRowAggregateRoot, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo]':
        """Construct a new Notion row from a given aggregate root."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def join_with_aggregate_root(
            self, aggregate_root: NotionRowAggregateRoot, extra_info: NotionRowDirectExtraInfo) \
            -> 'NotionRow[NotionRowAggregateRoot, NotionRowDirectExtraInfo, NotionRowInverseExtraInfo]':
        """Add to this Notion row from a given aggregate root."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def new_aggregate_root(self, extra_info: NotionRowInverseExtraInfo) -> NotionRowAggregateRoot:
        """Construct a new aggregate root from this notion row."""
        raise NotImplementedError("Can't use a base NotionRow class.")

    def apply_to_aggregate_root(
            self, aggregate_root: NotionRowAggregateRoot,
            extra_info: NotionRowInverseExtraInfo) -> NotionRowAggregateRoot:
        """Obtain the aggregate root form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")
