"""The command for computing stats."""

from jupiter.core.domain.application.stats.service.stats_service import StatsService
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.infer_sync_targets import (
    infer_sync_targets_for_enabled_features,
)
from jupiter.core.domain.sync_target import (
    SyncTarget,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class StatsDoArgs(UseCaseArgsBase):
    """StatsDoArgs."""

    today: ADate | None
    stats_targets: list[SyncTarget] | None
    filter_habit_ref_ids: list[EntityId] | None
    filter_big_plan_ref_ids: list[EntityId] | None
    filter_journal_ref_ids: list[EntityId] | None


@mutation_use_case()
class StatsDoUseCase(AppLoggedInMutationUseCase[StatsDoArgs, None]):
    """The command for computing stats."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: StatsDoArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace
        today = args.today or self._time_provider.get_current_date()

        stats_targets = (
            args.stats_targets
            if args.stats_targets is not None
            else infer_sync_targets_for_enabled_features(user, workspace, None)
        )

        stats_service = StatsService(
            domain_storage_engine=self._domain_storage_engine,
        )

        await stats_service.do_it(
            ctx=context.domain_context,
            progress_reporter=progress_reporter,
            user=user,
            workspace=workspace,
            today=today,
            stats_targets=stats_targets,
            filter_habit_ref_ids=args.filter_habit_ref_ids,
            filter_big_plan_ref_ids=args.filter_big_plan_ref_ids,
            filter_journal_ref_ids=args.filter_journal_ref_ids,
        )
