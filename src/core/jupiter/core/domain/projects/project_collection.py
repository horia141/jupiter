"""A project collection."""

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class ProjectCollection(TrunkEntity):
    """A project collection."""

    workspace_ref_id: EntityId

    projects = ContainsMany(Project, project_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_project_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "ProjectCollection":
        """Create a project collection."""
        return ProjectCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
