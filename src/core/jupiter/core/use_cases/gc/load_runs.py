"""Load previous runs of GC."""

from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)


@use_case_args
class GCLoadRunsArgs(UseCaseArgsBase):
    """GCLoadRunsArgs."""


@use_case_result
class GCLoadRunsResult(UseCaseResultBase):
    """GCLoadRunsResult."""

    entries: list[GCLogEntry]


@readonly_use_case()
class GCLoadRunsUseCase(AppLoggedInReadonlyUseCase[GCLoadRunsArgs, GCLoadRunsResult]):
    """Load previous runs of GC."""

    async def _execute(
        self,
        context: AppLoggedInReadonlyUseCaseContext,
        args: GCLoadRunsArgs,
    ) -> GCLoadRunsResult:
        """Execute the use case."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gc_log = await uow.gc_log_repository.load_by_parent(
                context.workspace.ref_id
            )
            entries = await uow.gc_log_entry_repository.find_last(gc_log.ref_id, 30)

        return GCLoadRunsResult(entries=entries)
