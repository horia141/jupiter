"""Load previous runs of GC."""
from dataclasses import dataclass

from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class GCLoadRunsArgs(UseCaseArgsBase):
    """GCLoadRunsArgs."""


@dataclass
class GCLoadRunsResult(UseCaseResultBase):
    """GCLoadRunsResult."""

    entries: list[GCLogEntry]


class GCLoadRunsUseCase(AppLoggedInReadonlyUseCase[GCLoadRunsArgs, GCLoadRunsResult]):
    """Load previous runs of GC."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: GCLoadRunsArgs,
    ) -> GCLoadRunsResult:
        """Execute the use case."""
        async with self._storage_engine.get_unit_of_work() as uow:
            gc_log = await uow.gc_log_repository.load_by_parent(
                context.workspace.ref_id
            )
            entries = await uow.gc_log_entry_repository.find_last(gc_log.ref_id, 30)

        return GCLoadRunsResult(entries=entries)
