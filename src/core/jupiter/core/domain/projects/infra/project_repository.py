"""A repository for projects."""

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class ProjectRepository(LeafEntityRepository[Project]):
    """A repository for projects."""
