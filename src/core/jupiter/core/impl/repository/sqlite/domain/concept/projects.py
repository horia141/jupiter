"""Implementation for projects repo via SQLite."""

from jupiter.core.domain.concept.projects.project import Project, ProjectRepository
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)


class SqliteProjectRepository(SqliteLeafEntityRepository[Project], ProjectRepository):
    """Sqlite implementation of the project repository."""

    async def load_root_project(self, parent_ref_id: EntityId) -> Project:
        """Load the root project."""
        projects = await self.find_all_generic(
            parent_ref_id=parent_ref_id,
            allow_archived=False,
            parent_project_ref_id=None,
        )

        if len(projects) == 0:
            raise Exception("Root project not found.")

        return projects[0]
