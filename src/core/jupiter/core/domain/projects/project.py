"""The project."""
import abc

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    ParentLink,
    RefsMany,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction


@entity
class Project(LeafEntity):
    """The project."""

    project_collection: ParentLink
    parent_project_ref_id: EntityId | None
    name: ProjectName
    order_of_child_projects: list[EntityId]

    inbox_tasks = RefsMany(InboxTask, project_ref_id=IsRefId())
    habits = RefsMany(Habit, project_ref_id=IsRefId())
    chores = RefsMany(Chore, project_ref_id=IsRefId())
    big_plans = RefsMany(BigPlan, project_ref_id=IsRefId())

    note = OwnsAtMostOne(
        Note, domain=NoteDomain.PROJECT, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_root_project(
        ctx: DomainContext,
        project_collection_ref_id: EntityId,
        name: ProjectName,
    ) -> "Project":
        """Create a root project."""
        return Project._create(
            ctx,
            project_collection=ParentLink(project_collection_ref_id),
            parent_project_ref_id=None,
            name=name,
            order_of_child_projects=[],
        )

    @staticmethod
    @create_entity_action
    def new_project(
        ctx: DomainContext,
        project_collection_ref_id: EntityId,
        parent_project_ref_id: EntityId,
        name: ProjectName,
    ) -> "Project":
        """Create a project."""
        return Project._create(
            ctx,
            project_collection=ParentLink(project_collection_ref_id),
            parent_project_ref_id=parent_project_ref_id,
            name=name,
            order_of_child_projects=[],
        )

    @update_entity_action
    def change_parent(
        self,
        ctx: DomainContext,
        parent_project_ref_id: EntityId,
    ) -> "Project":
        """Change the parent project of the project."""
        if self.is_root:
            raise Exception("Cannot change the parent of a root project.")
        return self._new_version(
            ctx,
            parent_project_ref_id=parent_project_ref_id,
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

    @update_entity_action
    def add_child_project(
        self,
        ctx: DomainContext,
        child_project_ref_id: EntityId,
    ) -> "Project":
        """Add a child project."""
        return self._new_version(
            ctx,
            order_of_child_projects=[
                *self.order_of_child_projects,
                child_project_ref_id,
            ],
        )

    @update_entity_action
    def remove_child_project(
        self,
        ctx: DomainContext,
        child_project_ref_id: EntityId,
    ) -> "Project":
        """Remove a child project."""
        return self._new_version(
            ctx,
            order_of_child_projects=[
                child_ref_id
                for child_ref_id in self.order_of_child_projects
                if child_ref_id != child_project_ref_id
            ],
        )

    @update_entity_action
    def reorder_child_projects(
        self,
        ctx: DomainContext,
        new_order: list[EntityId],
    ) -> "Project":
        """Reorder child projects."""
        return self._new_version(
            ctx,
            order_of_child_projects=new_order,
        )

    @property
    def is_root(self) -> bool:
        """Return True if this is a root project."""
        return self.parent_project_ref_id is None

    @property
    def surely_parent_project_ref_id(self) -> EntityId:
        """Return the parent ref id."""
        if self.parent_project_ref_id is None:
            raise Exception("This is a root project.")
        return self.parent_project_ref_id


class ProjectRepository(LeafEntityRepository[Project], abc.ABC):
    """A repository of projects."""

    @abc.abstractmethod
    async def load_root_project(self, parent_ref_id: EntityId) -> Project:
        """Load the root project."""
