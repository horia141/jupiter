"""The helpers are helping."""
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable, List

from jupiter.core.framework.entity import CrownEntity
from jupiter.core.framework.use_case import (
    EmptyContext,
    ProgressReporter,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import AppGuestMutationUseCaseContext


class NoOpProgressReporter(ProgressReporter):
    """A progress reporter that does nothing."""

    _created_entities: List[CrownEntity]
    _updated_entities: List[CrownEntity]
    _removed_entities: List[CrownEntity]

    def __init__(self) -> None:
        """Constructor."""
        self._created_entities = []
        self._updated_entities = []
        self._removed_entities = []

    @asynccontextmanager
    async def section(self, title: str) -> AsyncIterator[None]:
        """Start a section or subsection."""
        yield None

    async def mark_created(self, entity: CrownEntity) -> None:
        """Mark the entity as created."""
        self._created_entities.append(entity)

    async def mark_updated(self, entity: CrownEntity) -> None:
        """Mark the entity as updated."""
        self._updated_entities.append(entity)

    async def mark_removed(self, entity: CrownEntity) -> None:
        """Mark the entity as removed."""
        self._removed_entities.append(entity)

    @property
    def created_entities(self) -> Iterable[CrownEntity]:
        """Get all created entities."""
        return self._created_entities

    @property
    def updated_entities(self) -> Iterable[CrownEntity]:
        """Get all updated entities."""
        return self._updated_entities

    @property
    def removed_entities(self) -> Iterable[CrownEntity]:
        """Get all removed entities."""
        return self._removed_entities


class NoOpProgressReporterFactory(
    ProgressReporterFactory[AppGuestMutationUseCaseContext]
):
    """A noop progress reporter factory."""

    def new_reporter(self, context: AppGuestMutationUseCaseContext) -> ProgressReporter:
        """Construct a new progress reporter that does nothing."""
        return NoOpProgressReporter()


class EmptyProgressReporterFactory(ProgressReporterFactory[EmptyContext]):
    """A noop progress reporter factory."""

    def new_reporter(self, context: EmptyContext) -> ProgressReporter:
        """Construct a new progress reporter that does nothing."""
        return NoOpProgressReporter()
