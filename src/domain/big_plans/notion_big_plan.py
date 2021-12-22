"""A big plan on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from domain.adate import ADate
from domain.big_plans.big_plan import BigPlan
from domain.big_plans.big_plan_status import BigPlanStatus
from domain.entity_name import EntityName
from models.framework import BAD_NOTION_ID, NotionRow, EntityId


@dataclass()
class NotionBigPlan(NotionRow[BigPlan, None, 'NotionBigPlan.InverseExtraInfo']):
    """A big plan on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Extra info for the Notion to app sync."""
        big_plan_collection_ref_id: EntityId

    archived: bool
    name: str
    status: str
    due_date: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: BigPlan, extra_info: None) -> 'NotionBigPlan':
        """Construct a new Notion row from a given big plan."""
        return NotionBigPlan(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            status=aggregate_root.status.for_notion(),
            due_date=aggregate_root.due_date)

    def join_with_aggregate_root(self, aggregate_root: BigPlan, extra_info: None) -> 'NotionBigPlan':
        """Construct a Notion row from this and a big plan."""
        return NotionBigPlan(
            notion_id=self.notion_id,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            status=aggregate_root.status.for_notion(),
            due_date=aggregate_root.due_date)

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> BigPlan:
        """Create a new big plan from this."""
        return BigPlan.new_big_plan(
            archived=self.archived,
            big_plan_collection_ref_id=extra_info.big_plan_collection_ref_id,
            name=EntityName.from_raw(self.name),
            status=BigPlanStatus.from_raw(self.status),
            due_date=self.due_date,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: BigPlan, extra_info: InverseExtraInfo) -> BigPlan:
        """Apply to an already existing big plan."""
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_name(EntityName.from_raw(self.name), self.last_edited_time)
        aggregate_root.change_status(BigPlanStatus.from_raw(self.status), self.last_edited_time)
        aggregate_root.change_due_date(self.due_date, self.last_edited_time)
        return aggregate_root
