"""A repository for projects."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class ProjectRepository(LeafEntityRepository[Project]):
    """A repository for projects."""
