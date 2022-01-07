"""A big plan on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionBigPlan(NotionRow[BigPlan, None, 'NotionBigPlan.InverseExtraInfo']):
    """A big plan on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Extra info for the Notion to app sync."""
        big_plan_collection_ref_id: EntityId

    name: str
    status: str
    actionable_date: Optional[ADate]
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
            actionable_date=aggregate_root.actionable_date,
            due_date=aggregate_root.due_date)

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> BigPlan:
        """Create a new big plan from this."""
        return BigPlan.new_big_plan(
            archived=self.archived,
            big_plan_collection_ref_id=extra_info.big_plan_collection_ref_id,
            name=BigPlanName.from_raw(self.name),
            status=BigPlanStatus.from_raw(self.status),
            actionable_date=self.actionable_date,
            due_date=self.due_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: BigPlan, extra_info: InverseExtraInfo) -> BigPlan:
        """Apply to an already existing big plan."""
        aggregate_root.update(
            name=UpdateAction.change_to(BigPlanName.from_raw(self.name)),
            status=UpdateAction.change_to(BigPlanStatus.from_raw(self.status)),
            actionable_date=UpdateAction.change_to(self.actionable_date),
            due_date=UpdateAction.change_to(self.due_date),
            source=EventSource.NOTION,
            modification_time=self.last_edited_time)
        aggregate_root.change_archived(
            archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
        return aggregate_root
