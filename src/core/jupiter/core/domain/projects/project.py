"""The project."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    ParentLink,
    RefsMany,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class Project(LeafEntity):
    """The project."""

    project_collection: ParentLink
    name: ProjectName

    inbox_tasks = RefsMany(InboxTask, project_ref_id=IsRefId())
    habits = RefsMany(Habit, project_ref_id=IsRefId())
    chores = RefsMany(Chore, project_ref_id=IsRefId())
    big_plans = RefsMany(BigPlan, project_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_project(
        ctx: DomainContext,
        project_collection_ref_id: EntityId,
        name: ProjectName,
    ) -> "Project":
        """Create a project."""
        return Project._create(
            ctx,
            project_collection=ParentLink(project_collection_ref_id),
            name=name,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[ProjectName],
    ) -> "Project":
        """Change the project."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )
