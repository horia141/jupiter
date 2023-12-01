"""The command for doing task generation for all workspaces."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.gen.service.gen_service import GenService
from jupiter.core.domain.storage_engine import DomainStorageEngine
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
class GenDoAllArgs(UseCaseArgsBase):
    """GenDoAllArgs."""


class GenDoAllUseCase(AppBackgroundMutationUseCase[GenDoAllArgs, None]):
    """The command for doing task generation for all workspaces."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        progress_reporter_factory: ProgressReporterFactory[EmptyContext],
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(progress_reporter_factory)
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: EmptyContext,
        args: GenDoAllArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            workspaces = await uow.workspace_repository.find_all(allow_archived=False)
            users = await uow.user_repository.find_all(allow_archived=False)
            users_by_id = {u.ref_id: u for u in users}
            user_workspace_links = await uow.user_workspace_link_repository.find_all(
                allow_archived=False
            )
            users_id_by_workspace_id = {
                uwl.workspace_ref_id: uwl.user_ref_id for uwl in user_workspace_links
            }

        gen_service = GenService(
            source=EventSource.GEN_CRON,
            time_provider=self._time_provider,
            domain_storage_engine=self._storage_engine,
        )

        today = self._time_provider.get_current_date()

        for workspace in workspaces:
            user = users_by_id[users_id_by_workspace_id[workspace.ref_id]]
            gen_targets = workspace.infer_sync_targets_for_enabled_features(None)
            await gen_service.do_it(
                user=user,
                progress_reporter=progress_reporter,
                workspace=workspace,
                gen_even_if_not_modified=False,
                today=today,
                gen_targets=gen_targets,
                period=None,
                filter_project_ref_ids=None,
                filter_habit_ref_ids=None,
                filter_chore_ref_ids=None,
                filter_metric_ref_ids=None,
                filter_person_ref_ids=None,
                filter_slack_task_ref_ids=None,
                filter_email_task_ref_ids=None,
            )
