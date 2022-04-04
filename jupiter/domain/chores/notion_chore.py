"""A chore on Notion-side."""
from dataclasses import dataclass
from typing import Optional, Dict

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.chore_name import ChoreName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction
from jupiter.remote.notion.common import format_name_for_option


@dataclass(frozen=True)
class NotionChore(
    NotionLeafEntity[Chore, "NotionChore.DirectInfo", "NotionChore.InverseInfo"]
):
    """A chore on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""

        all_projects_map: Dict[EntityId, Project]

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from Notion to app side."""

        default_project: Project
        all_projects_by_name: Dict[str, Project]
        all_projects_map: Dict[EntityId, Project]

    name: str
    period: Optional[str]
    eisen: Optional[str]
    difficulty: Optional[str]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    must_do: bool
    skip_rule: Optional[str]
    start_at_date: Optional[ADate]
    end_at_date: Optional[ADate]
    project_ref_id: Optional[str]
    project_name: Optional[str]

    @staticmethod
    def new_notion_entity(entity: Chore, extra_info: DirectInfo) -> "NotionChore":
        """Construct a new Notion row from a given chore."""
        return NotionChore(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            name=str(entity.name),
            period=entity.gen_params.period.for_notion(),
            eisen=entity.gen_params.eisen.for_notion(),
            difficulty=entity.gen_params.difficulty.for_notion()
            if entity.gen_params.difficulty
            else None,
            actionable_from_day=entity.gen_params.actionable_from_day.as_int()
            if entity.gen_params.actionable_from_day
            else None,
            actionable_from_month=entity.gen_params.actionable_from_month.as_int()
            if entity.gen_params.actionable_from_month
            else None,
            due_at_time=str(entity.gen_params.due_at_time)
            if entity.gen_params.due_at_time
            else None,
            due_at_day=entity.gen_params.due_at_day.as_int()
            if entity.gen_params.due_at_day
            else None,
            due_at_month=entity.gen_params.due_at_month.as_int()
            if entity.gen_params.due_at_month
            else None,
            skip_rule=str(entity.skip_rule),
            start_at_date=entity.start_at_date,
            end_at_date=entity.end_at_date,
            suspended=entity.suspended,
            must_do=entity.must_do,
            project_ref_id=str(entity.project_ref_id),
            project_name=format_name_for_option(
                extra_info.all_projects_map[entity.project_ref_id].name
            ),
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: InverseInfo) -> Chore:
        """Create a new chore from this."""
        chore_period = RecurringTaskPeriod.from_raw(self.period)

        project_ref_id = (
            EntityId.from_raw(self.project_ref_id) if self.project_ref_id else None
        )
        project_name = (
            ProjectName.from_raw(self.project_name) if self.project_name else None
        )

        if project_ref_id is not None:
            project = extra_info.all_projects_map[project_ref_id]
        elif project_name is not None:
            project = extra_info.all_projects_by_name[
                format_name_for_option(project_name)
            ]
        else:
            project = extra_info.default_project

        return Chore.new_chore(
            chore_collection_ref_id=parent_ref_id,
            project_ref_id=project.ref_id,
            archived=self.archived,
            name=ChoreName.from_raw(self.name),
            gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(self.period),
                eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                difficulty=Difficulty.from_raw(self.difficulty)
                if self.difficulty
                else None,
                actionable_from_day=RecurringTaskDueAtDay.from_raw(
                    chore_period, self.actionable_from_day
                )
                if self.actionable_from_day
                else None,
                actionable_from_month=RecurringTaskDueAtMonth.from_raw(
                    chore_period, self.actionable_from_month
                )
                if self.actionable_from_month
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time)
                if self.due_at_time
                else None,
                due_at_day=RecurringTaskDueAtDay.from_raw(chore_period, self.due_at_day)
                if self.due_at_day
                else None,
                due_at_month=RecurringTaskDueAtMonth.from_raw(
                    chore_period, self.due_at_month
                )
                if self.due_at_month
                else None,
            ),
            suspended=self.suspended,
            must_do=self.must_do,
            skip_rule=RecurringTaskSkipRule.from_raw(self.skip_rule)
            if self.skip_rule
            else None,
            start_at_date=self.start_at_date,
            end_at_date=self.end_at_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: Chore, extra_info: InverseInfo
    ) -> NotionLeafApplyToEntityResult[Chore]:
        """Apply to an already existing chore."""
        should_modify_on_notion = False
        chore_period = RecurringTaskPeriod.from_raw(self.period)

        project_ref_id = (
            EntityId.from_raw(self.project_ref_id) if self.project_ref_id else None
        )
        project_name = (
            ProjectName.from_raw(self.project_name) if self.project_name else None
        )

        if project_ref_id is not None:
            project = extra_info.all_projects_map[project_ref_id]
        elif project_name is not None:
            should_modify_on_notion = True
            project = extra_info.all_projects_by_name[
                format_name_for_option(project_name)
            ]
        else:
            should_modify_on_notion = True
            project = extra_info.default_project

        good_start_at_date = self.start_at_date
        if good_start_at_date is None:
            good_start_at_date = entity.start_at_date
            should_modify_on_notion = True

        new_entity = entity.change_project(
            project_ref_id=project.ref_id,
            source=EventSource.NOTION,
            modification_time=self.last_edited_time,
        ).update(
            name=UpdateAction.change_to(ChoreName.from_raw(self.name)),
            gen_params=UpdateAction.change_to(
                RecurringTaskGenParams(
                    period=RecurringTaskPeriod.from_raw(self.period),
                    eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                    difficulty=Difficulty.from_raw(self.difficulty)
                    if self.difficulty
                    else None,
                    actionable_from_day=RecurringTaskDueAtDay.from_raw(
                        chore_period, self.actionable_from_day
                    )
                    if self.actionable_from_day
                    else None,
                    actionable_from_month=RecurringTaskDueAtMonth.from_raw(
                        chore_period, self.actionable_from_month
                    )
                    if self.actionable_from_month
                    else None,
                    due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time)
                    if self.due_at_time
                    else None,
                    due_at_day=RecurringTaskDueAtDay.from_raw(
                        chore_period, self.due_at_day
                    )
                    if self.due_at_day
                    else None,
                    due_at_month=RecurringTaskDueAtMonth.from_raw(
                        chore_period, self.due_at_month
                    )
                    if self.due_at_month
                    else None,
                )
            ),
            must_do=UpdateAction.change_to(self.must_do),
            skip_rule=UpdateAction.change_to(
                RecurringTaskSkipRule.from_raw(self.skip_rule)
                if self.skip_rule
                else None
            ),
            start_at_date=UpdateAction.change_to(
                self.start_at_date if self.start_at_date else entity.start_at_date
            ),
            end_at_date=UpdateAction.change_to(self.end_at_date),
            source=EventSource.NOTION,
            modification_time=self.last_edited_time,
        )
        if self.suspended:
            new_entity = new_entity.suspend(
                source=EventSource.NOTION, modification_time=self.last_edited_time
            )
        else:
            new_entity = new_entity.unsuspend(
                source=EventSource.NOTION, modification_time=self.last_edited_time
            )
        new_entity = new_entity.change_archived(
            archived=self.archived,
            source=EventSource.NOTION,
            archived_time=self.last_edited_time,
        )

        return NotionLeafApplyToEntityResult(new_entity, should_modify_on_notion)

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return self.name
