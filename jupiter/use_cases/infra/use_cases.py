"""Jupiter specific use cases classes."""
import abc
from dataclasses import dataclass
from typing import Generic, Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    UseCaseArgs,
    UseCaseResult,
    MutationUseCase,
    MutationUseCaseInvocationRecorder,
    ReadonlyUseCase,
    UseCaseContextBase,
)
from jupiter.utils.time_provider import TimeProvider


@dataclass(frozen=True)
class AppUseCaseContext(UseCaseContextBase):
    """The application use case context."""

    workspace: Workspace

    @property
    def owner_ref_id(self) -> EntityId:
        """The owner root entity id."""
        return self.workspace.ref_id


class AppMutationUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    MutationUseCase[AppUseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation for the app."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder)
        self._storage_engine = storage_engine

    def _build_context(self) -> AppUseCaseContext:
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            return AppUseCaseContext(workspace)


class AppReadonlyUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    ReadonlyUseCase[AppUseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation for the app."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        super().__init__()
        self._storage_engine = storage_engine

    def _build_context(self) -> AppUseCaseContext:
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            return AppUseCaseContext(workspace)
