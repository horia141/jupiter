"""A big plan collection on Notion-side."""
from dataclasses import dataclass

from domain.big_plans.big_plan_collection import BigPlanCollection
from domain.timestamp import Timestamp
from models.framework import NotionEntity, BAD_NOTION_ID


@dataclass()
class NotionBigPlanCollection(NotionEntity[BigPlanCollection]):
    """A big plan collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: BigPlanCollection) -> 'NotionBigPlanCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionBigPlanCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def join_with_aggregate_root(self, aggregate_root: BigPlanCollection) -> 'NotionBigPlanCollection':
        """Add to this Notion row from a given aggregate root."""
        return NotionBigPlanCollection(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: BigPlanCollection, modification_time: Timestamp) -> BigPlanCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root
