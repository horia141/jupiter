"""The command for doing garbage collection for all workspaces."""

from jupiter.core.domain.gc.service.gc_service import GCService
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    EmptyContext,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppBackgroundMutationUseCase


@use_case_args
class GCDoAllArgs(UseCaseArgsBase):
    """GCDoAllArgs."""


class GCDoAllUseCase(AppBackgroundMutationUseCase[GCDoAllArgs, None]):
    """The command for doing garbage collection for all workspaces."""

    async def _execute(
        self,
        context: EmptyContext,
        args: GCDoAllArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspaces = await uow.get_for(Workspace).find_all(
                allow_archived=False
            )

        ctx = DomainContext(EventSource.GC_CRON, self._time_provider.get_current_time())

        gc_service = GCService(
            domain_storage_engine=self._domain_storage_engine,
        )

        for workspace in workspaces:
            progress_reporter = self._progress_reporter_factory.new_reporter(context)
            gc_targets = workspace.infer_sync_targets_for_enabled_features(None)
            await gc_service.do_it(ctx, progress_reporter, workspace, gc_targets)

            async with self._search_storage_engine.get_unit_of_work() as search_uow:
                for created_entity in progress_reporter.created_entities:
                    await search_uow.search_repository.create(
                        workspace.ref_id, created_entity
                    )

                for updated_entity in progress_reporter.updated_entities:
                    await search_uow.search_repository.update(
                        workspace.ref_id, updated_entity
                    )

                for removed_entity in progress_reporter.removed_entities:
                    await search_uow.search_repository.remove(
                        workspace.ref_id, removed_entity
                    )
