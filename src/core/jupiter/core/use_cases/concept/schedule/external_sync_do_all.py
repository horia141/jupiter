"""The commnad for syncing a schedule once."""
from jupiter.core.domain.concept.schedule.service.external_sync_service import ScheduleExternalSyncService
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.user_workspace_link.user_workspace_link import UserWorkspaceLink
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import EmptyContext
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppBackgroundMutationUseCase


@use_case_args
class ScheduleExternalSyncDoAllArgs(UseCaseArgsBase):
    """ScheduleExternalSyncDoArgs."""

class ScheduleExternalSyncDoAllUseCase(AppBackgroundMutationUseCase[ScheduleExternalSyncDoAllArgs, None]):
    """The command for doing a sync."""

    async def _execute(self, context: EmptyContext, args: ScheduleExternalSyncDoAllArgs) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspaces = await uow.get_for(Workspace).find_all(allow_archived=False)

        ctx = DomainContext(
            EventSource.SCHEDULE_EXTERNAL_SYNC_CRON, self._time_provider.get_current_time()
        )

        sync_service = ScheduleExternalSyncService(
            time_provider=self._time_provider,
            realm_codec_registry=self._realm_codec_registry,
            domain_storage_engine=self._domain_storage_engine,
        )

        for workspace in workspaces:
            progress_reporter = self._progress_reporter_factory.new_reporter(context)
            await sync_service.do_it(
                ctx=ctx,
                progress_reporter=progress_reporter,
                workspace=workspace,
                filter_schedule_stream_ref_id=None,
            )

            async with self._search_storage_engine.get_unit_of_work() as search_uow:
                for created_entity in progress_reporter.created_entities:
                    await search_uow.search_repository.upsert(workspace.ref_id, created_entity)

                for updated_entity in progress_reporter.updated_entities:
                    await search_uow.search_repository.upsert(workspace.ref_id, updated_entity)

                for deleted_entity in progress_reporter.removed_entities:
                    await search_uow.search_repository.remove(workspace.ref_id, deleted_entity)
