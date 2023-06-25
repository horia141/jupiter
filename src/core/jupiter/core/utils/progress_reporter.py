"""The helpers are helping."""
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    EmptyContext,
    EntityProgressReporter,
    MarkProgressStatus,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseContext


class NoOpEntityProgressReporter(EntityProgressReporter):
    """A progress reporter that does nothing."""

    async def mark_not_needed(self) -> "NoOpEntityProgressReporter":
        """Mark the fact that a particular modification isn't needed."""
        return self

    async def mark_known_entity_id(
        self,
        entity_id: EntityId,
    ) -> "NoOpEntityProgressReporter":
        """Mark the fact that we now know the entity id for the entity being processed."""
        return self

    async def mark_known_name(self, name: str) -> "NoOpEntityProgressReporter":
        """Mark the fact that we now know the entity name for the entity being processed."""
        return self

    async def mark_local_change(self) -> "NoOpEntityProgressReporter":
        """Mark the fact that the local change has succeeded."""
        return self

    async def mark_remote_change(
        self,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> "NoOpEntityProgressReporter":
        """Mark the fact that the remote change has completed."""
        return self

    async def mark_other_progress(
        self,
        progress: str,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> "NoOpEntityProgressReporter":
        """Mark some other type of progress."""
        return self


class NoOpContextProgressReporter(ContextProgressReporter):
    """A progress reporter that does nothing."""

    @asynccontextmanager
    async def section(self, title: str) -> AsyncIterator[None]:
        """Start a section or subsection."""
        yield None

    @asynccontextmanager
    async def start_creating_entity(
        self,
        entity_type: str,
        entity_name: str,
    ) -> AsyncIterator[NoOpEntityProgressReporter]:
        """Report that a particular entity is being created."""
        yield NoOpEntityProgressReporter()

    @asynccontextmanager
    async def start_updating_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[NoOpEntityProgressReporter]:
        """Report that a particular entity is being updated."""
        yield NoOpEntityProgressReporter()

    @asynccontextmanager
    async def start_archiving_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[NoOpEntityProgressReporter]:
        """Report that a particular entity is being archived."""
        yield NoOpEntityProgressReporter()

    @asynccontextmanager
    async def start_removing_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[NoOpEntityProgressReporter]:
        """Report that a particular entity is being removed."""
        yield NoOpEntityProgressReporter()

    @asynccontextmanager
    async def start_complex_entity_work(
        self,
        entity_type: str,
        entity_id: EntityId,
        entity_name: str,
    ) -> AsyncIterator["NoOpContextProgressReporter"]:
        """Create a progress reporter with some scoping to operate with subentities of a main entity."""
        yield NoOpContextProgressReporter()


class NoOpProgressReporterFactory(ProgressReporterFactory[AppGuestUseCaseContext]):
    """A noop progress reporter factory."""

    def new_reporter(self, context: AppGuestUseCaseContext) -> ContextProgressReporter:
        """Construct a new progress reporter that does nothing."""
        return NoOpContextProgressReporter()


class EmptyProgressReporterFactory(ProgressReporterFactory[EmptyContext]):
    """A noop progress reporter factory."""

    def new_reporter(self, context: EmptyContext) -> ContextProgressReporter:
        """Construct a new progress reporter that does nothing."""
        return NoOpContextProgressReporter()
