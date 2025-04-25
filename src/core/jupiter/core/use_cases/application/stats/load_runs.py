"""Load previous runs of stats computation."""

from jupiter.core.domain.application.stats.stats_log import StatsLog
from jupiter.core.domain.application.stats.stats_log_entry import (
    StatsLogEntry,
    StatsLogEntryRepository,
)
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
class StatsLoadRunsArgs(UseCaseArgsBase):
    """StatsLoadRunsArgs."""


@use_case_result
class StatsLoadRunsResult(UseCaseResultBase):
    """StatsLoadRunsResult."""

    entries: list[StatsLogEntry]


@readonly_use_case()
class StatsLoadRunsUseCase(
    AppLoggedInReadonlyUseCase[StatsLoadRunsArgs, StatsLoadRunsResult]
):
    """Load previous runs of stats computation."""

    async def _execute(
        self,
        context: AppLoggedInReadonlyUseCaseContext,
        args: StatsLoadRunsArgs,
    ) -> StatsLoadRunsResult:
        """Execute the use case."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            stats_log = await uow.get_for(StatsLog).load_by_parent(
                context.workspace.ref_id
            )
            entries = await uow.get(StatsLogEntryRepository).find_last(
                stats_log.ref_id, 30
            )

        return StatsLoadRunsResult(entries=entries)
