"""Use case for syncing a schedule once."""

from jupiter.core.domain.concept.schedule.service.external_sync_service import (
    ScheduleExternalSyncService,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class ScheduleExternalSyncDoArgs(UseCaseArgsBase):
    """ScheduleExternalSyncDoArgs."""

    today: ADate | None
    sync_even_if_not_modified: bool
    filter_schedule_stream_ref_id: list[EntityId] | None


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleExternalSyncDoUseCase(
    AppLoggedInMutationUseCase[ScheduleExternalSyncDoArgs, None]
):
    """The command for doing a sync."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleExternalSyncDoArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        sync_service = ScheduleExternalSyncService(
            time_provider=self._time_provider,
            realm_codec_registry=self._realm_codec_registry,
            domain_storage_engine=self._domain_storage_engine,
        )
        today = args.today or self._time_provider.get_current_date()
        await sync_service.do_it(
            context.domain_context,
            progress_reporter,
            workspace,
            today,
            args.sync_even_if_not_modified,
            args.filter_schedule_stream_ref_id,
        )
