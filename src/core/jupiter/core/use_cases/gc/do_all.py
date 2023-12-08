"""The command for doing garbage collection for all workspaces."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.gc.service.gc_service import GCService
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    EmptyContext,
    ProgressReporter,
    ProgressReporterFactory,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import AppBackgroundMutationUseCase
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class GCDoAllArgs(UseCaseArgsBase):
    """GCDoAllArgs."""


class GCDoAllUseCase(AppBackgroundMutationUseCase[GCDoAllArgs, None]):
    """The command for doing garbage collection for all workspaces."""

    _time_provider: Final[TimeProvider]
    _domain_storage_engine: Final[DomainStorageEngine]
    _search_storage_engine: Final[SearchStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        progress_reporter_factory: ProgressReporterFactory[EmptyContext],
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(progress_reporter_factory)
        self._time_provider = time_provider
        self._domain_storage_engine = domain_storage_engine
        self._search_storage_engine = search_storage_engine

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: EmptyContext,
        args: GCDoAllArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspaces = await uow.workspace_repository.find_all(allow_archived=False)

        gc_service = GCService(
            source=EventSource.GC_CRON,
            time_provider=self._time_provider,
            domain_storage_engine=self._domain_storage_engine,
            search_storage_engine=self._search_storage_engine,
        )

        for workspace in workspaces:
            gc_targets = workspace.infer_sync_targets_for_enabled_features(None)
            await gc_service.do_it(progress_reporter, workspace, gc_targets)
