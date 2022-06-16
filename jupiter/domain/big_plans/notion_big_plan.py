"""A big plan on Notion-side."""
from dataclasses import dataclass
from typing import Optional, Dict

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction
from jupiter.remote.notion.common import format_name_for_option


@dataclass(frozen=True)
class NotionBigPlan(
    NotionLeafEntity[BigPlan, "NotionBigPlan.DirectInfo", "NotionBigPlan.InverseInfo"]
):
    """A big plan on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""

        all_projects_map: Dict[EntityId, Project]

    @dataclass(frozen=True)
    class InverseInfo:
        """Extra info for the Notion to app sync."""

        default_project: Project
        all_projects_by_name: Dict[str, Project]
        all_projects_map: Dict[EntityId, Project]

    name: str
    status: Optional[str]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    project_ref_id: Optional[str]
    project_name: Optional[str]

    @staticmethod
    def new_notion_entity(entity: BigPlan, extra_info: DirectInfo) -> "NotionBigPlan":
        """Construct a new Notion row from a given big plan."""
        return NotionBigPlan(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            name=str(entity.name),
            status=entity.status.for_notion(),
            actionable_date=entity.actionable_date,
            due_date=entity.due_date,
            project_ref_id=str(entity.project_ref_id),
            project_name=format_name_for_option(
                extra_info.all_projects_map[entity.project_ref_id].name
            ),
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: InverseInfo) -> BigPlan:
        """Create a new big plan from this."""
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

        return BigPlan.new_big_plan(
            archived=self.archived,
            big_plan_collection_ref_id=parent_ref_id,
            project_ref_id=project.ref_id,
            name=BigPlanName.from_raw(self.name),
            status=BigPlanStatus.from_raw(self.status)
            if self.status
            else BigPlanStatus.NOT_STARTED,
            actionable_date=self.actionable_date,
            due_date=self.due_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: BigPlan, extra_info: InverseInfo
    ) -> NotionLeafApplyToEntityResult[BigPlan]:
        """Apply to an already existing big plan."""
        should_modify_on_notion = False
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
            should_modify_on_notion = True
        else:
            project = extra_info.default_project
            should_modify_on_notion = True

        clean_status = None
        if self.status:
            clean_status = BigPlanStatus.from_raw(self.status)
        else:
            clean_status = BigPlanStatus.NOT_STARTED
            should_modify_on_notion = True

        new_entity = (
            entity.change_project(
                project_ref_id=project.ref_id,
                source=EventSource.NOTION,
                modification_time=self.last_edited_time,
            )
            .update(
                name=UpdateAction.change_to(BigPlanName.from_raw(self.name)),
                status=UpdateAction.change_to(clean_status),
                actionable_date=UpdateAction.change_to(self.actionable_date),
                due_date=UpdateAction.change_to(self.due_date),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time,
            )
            .change_archived(
                archived=self.archived,
                source=EventSource.NOTION,
                archived_time=self.last_edited_time,
            )
        )

        return NotionLeafApplyToEntityResult(new_entity, should_modify_on_notion)

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return self.name
