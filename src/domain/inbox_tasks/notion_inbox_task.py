"""A inbox task on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List, Dict

from domain.adate import ADate
from domain.big_plan_essentials import BigPlanEssentials
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from framework.errors import ModelValidationError
from framework.base.entity_id import EntityId
from framework.notion import NotionRow, BAD_NOTION_ID
from remote.notion.common import format_name_for_option


@dataclass(frozen=True)
class NotionInboxTask(NotionRow[InboxTask, 'NotionInboxTask.DirectInfo', 'NotionInboxTask.InverseInfo']):
    """A inbox task on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""
        big_plan_name: Optional[EntityName]

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from Notion to the app."""
        inbox_task_collection_ref_id: EntityId
        all_big_plans_by_name: Dict[str, BigPlanEssentials]
        all_big_plans_map: Dict[EntityId, BigPlanEssentials]

    source: str
    name: str
    archived: bool
    big_plan_ref_id: Optional[str]
    big_plan_name: Optional[str]
    recurring_task_ref_id: Optional[str]
    metric_ref_id: Optional[str]
    person_ref_id: Optional[str]
    status: Optional[str]
    eisen: Optional[List[str]]
    difficulty: Optional[str]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    from_script: bool
    recurring_timeline: Optional[str]
    recurring_period: Optional[str]
    recurring_type: Optional[str]
    recurring_gen_right_now: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: InboxTask, extra_info: DirectInfo) -> 'NotionInboxTask':
        """Construct a new Notion row from a given inbox task."""
        return NotionInboxTask(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            source=aggregate_root.source.for_notion(),
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            big_plan_ref_id=str(aggregate_root.big_plan_ref_id) if aggregate_root.big_plan_ref_id else None,
            big_plan_name=format_name_for_option(extra_info.big_plan_name) if extra_info.big_plan_name else None,
            recurring_task_ref_id=
            str(aggregate_root.recurring_task_ref_id) if aggregate_root.recurring_task_ref_id else None,
            metric_ref_id=str(aggregate_root.metric_ref_id) if aggregate_root.metric_ref_id else None,
            person_ref_id=str(aggregate_root.person_ref_id) if aggregate_root.person_ref_id else None,
            status=aggregate_root.status.for_notion(),
            eisen=[e.for_notion() for e in aggregate_root.eisen],
            difficulty=aggregate_root.difficulty.for_notion() if aggregate_root.difficulty else None,
            actionable_date=aggregate_root.actionable_date,
            due_date=aggregate_root.due_date,
            from_script=aggregate_root.source.is_from_script,
            recurring_timeline=aggregate_root.recurring_timeline,
            recurring_period=aggregate_root.recurring_period.for_notion() if aggregate_root.recurring_period else None,
            recurring_type=aggregate_root.recurring_type.for_notion() if aggregate_root.recurring_type else None,
            recurring_gen_right_now=
            ADate.from_timestamp(aggregate_root.recurring_gen_right_now)
            if aggregate_root.recurring_gen_right_now else None)

    def new_aggregate_root(self, extra_info: InverseInfo) -> InboxTask:
        """Create a new inbox task from this."""
        inbox_task_name = EntityName.from_raw(self.name)
        inbox_task_big_plan_ref_id = \
            EntityId.from_raw(self.big_plan_ref_id) \
                if self.big_plan_ref_id else None
        inbox_task_big_plan_name = EntityName.from_raw(self.big_plan_name) \
            if self.big_plan_name else None
        inbox_task_recurring_task_ref_id = \
            EntityId.from_raw(self.recurring_task_ref_id) \
                if self.recurring_task_ref_id else None
        inbox_task_metric_ref_id = \
            EntityId.from_raw(self.metric_ref_id) \
                if self.metric_ref_id else None
        inbox_task_person_ref_id = \
            EntityId.from_raw(self.person_ref_id) \
                if self.person_ref_id else None
        inbox_task_status = \
            InboxTaskStatus.from_raw(self.status) \
                if self.status else InboxTaskStatus.NOT_STARTED
        inbox_task_eisen = \
            [Eisen.from_raw(e) for e in self.eisen] \
                if self.eisen else []
        inbox_task_difficulty = \
            Difficulty.from_raw(self.difficulty) \
                if self.difficulty else None

        big_plan = None
        if inbox_task_big_plan_ref_id is not None:
            big_plan = extra_info.all_big_plans_map[inbox_task_big_plan_ref_id]
        elif inbox_task_big_plan_name is not None:
            big_plan = \
                extra_info.all_big_plans_by_name[format_name_for_option(inbox_task_big_plan_name)]
        elif inbox_task_recurring_task_ref_id is not None:
            raise ModelValidationError("Trying to create an inbox task for a recurring task from Notion")
        elif inbox_task_metric_ref_id is not None:
            raise ModelValidationError("Trying to create an inbox task for a metric from Notion")
        elif inbox_task_person_ref_id is not None:
            raise ModelValidationError("Trying to create an inbox task for a person from Notion")

        return InboxTask.new_inbox_task(
            inbox_task_collection_ref_id=extra_info.inbox_task_collection_ref_id,
            archived=self.archived,
            name=inbox_task_name,
            status=inbox_task_status,
            big_plan_ref_id=big_plan.ref_id if big_plan else None,
            eisen=inbox_task_eisen,
            difficulty=inbox_task_difficulty,
            actionable_date=self.actionable_date,
            due_date=self.due_date,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: InboxTask, extra_info: InverseInfo) -> InboxTask:
        """Apply to an already existing inbox task."""
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_status(
            InboxTaskStatus.from_raw(self.status) if self.status else InboxTaskStatus.NOT_STARTED,
            self.last_edited_time)
        if aggregate_root.source.allow_user_changes:
            aggregate_root.change_name(EntityName.from_raw(self.name), self.last_edited_time)
            aggregate_root.change_eisen(
                [Eisen.from_raw(e) for e in self.eisen] if self.eisen else [], self.last_edited_time)
            aggregate_root.change_difficulty(
                Difficulty.from_raw(self.difficulty) if self.difficulty else None, self.last_edited_time)
            aggregate_root.change_actionable_date(self.actionable_date, self.last_edited_time)
            aggregate_root.change_due_date(self.due_date, self.last_edited_time)

        return aggregate_root
