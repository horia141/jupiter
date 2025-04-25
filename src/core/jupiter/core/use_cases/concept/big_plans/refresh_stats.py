"""A use case for refreshing stats for a big plan."""

from jupiter.core.domain.application.stats.service.stats_service import StatsService
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class BigPlanRefreshStatsArgs(UseCaseArgsBase):
    """The arguments for the big plan refresh stats use case."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanRefreshStatsUseCase(
    AppLoggedInMutationUseCase[BigPlanRefreshStatsArgs, None]
):
    """A use case for refreshing stats for a big plan."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanRefreshStatsArgs,
    ) -> None:
        """Perform the mutation."""
        stats_service = StatsService(
            domain_storage_engine=self._domain_storage_engine,
        )

        await stats_service.do_it(
            ctx=context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            today=self._time_provider.get_current_date(),
            stats_targets=[SyncTarget.BIG_PLANS],
            filter_big_plan_ref_ids=[args.ref_id],
            filter_habit_ref_ids=None,
            filter_journal_ref_ids=None,
        )
