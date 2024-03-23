"""A service that checks for cycles in the project graph."""
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId


class ProjectTreeHasCyclesError(Exception):
    """Exception raised when the project tree has cycles."""


class ProjectCheckCyclesService:
    """A service that checks for cycles in the project graph."""

    async def check_for_cycles(self, uow: DomainUnitOfWork, project: Project) -> None:
        """Check for cycles in the project graph."""
        if project.parent_project_ref_id is None:
            return

        current_ref_id: EntityId | None = project.parent_project_ref_id

        while current_ref_id is not None:
            if current_ref_id == project.ref_id:
                raise ProjectTreeHasCyclesError
            current_project = await uow.get_for(Project).load_by_id(current_ref_id)
            current_ref_id = current_project.parent_project_ref_id
