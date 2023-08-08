"""A search index repository for free form searching across all entities in Jupiter."""
import abc
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.repository import Repository


@dataclass
class SearchMatch:
    """Information about a particular entity that was found."""

    entity_tag: NamedEntityTag
    ref_id: EntityId
    name: EntityName
    archived: bool
    match_highlight: str
    match_snippet: str
    search_rank: float  # lower is better


class SearchRepository(Repository, abc.ABC):
    """A search index repository for free form searching across all entities."""

    @abc.abstractmethod
    async def create(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Add an entity and make it available for searching."""

    @abc.abstractmethod
    async def update(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Update an entity for searching."""

    @abc.abstractmethod
    async def remove(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Remove an entity from the search index."""

    @abc.abstractmethod
    async def drop(self) -> None:
        """Remove all entries from the search index."""

    @abc.abstractmethod
    async def search(
        self,
        workspace_ref_id: EntityId,
        query: str,
        limit: int,
        include_archived: bool,
        filter_entity_tags: Optional[Iterable[NamedEntityTag]],
    ) -> List[SearchMatch]:
        """Search for entities"""
