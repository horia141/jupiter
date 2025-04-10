"""The command for doing task generation for all workspaces."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    EmptyContext,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    SysBackgroundMutationUseCase,
)


@use_case_args
class GenDoAllArgs(UseCaseArgsBase):
    """GenDoAllArgs."""


class GenDoAllUseCase(SysBackgroundMutationUseCase[GenDoAllArgs, None]):
    """The command for doing task generation for all workspaces."""

    async def _execute(self, context: EmptyContext, args: GenDoAllArgs) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspaces = await uow.get_for(Workspace).find_all(allow_archived=False)
            users = await uow.get_for(User).find_all(allow_archived=False)
            users_by_id = {u.ref_id: u for u in users}
            user_workspace_links = await uow.get_for(UserWorkspaceLink).find_all(
                allow_archived=False
            )
            users_id_by_workspace_id = {
                uwl.workspace_ref_id: uwl.user_ref_id for uwl in user_workspace_links
            }

        ctx = DomainContext.from_sys(
            EventSource.GEN_CRON, self._time_provider.get_current_time()
        )

        gen_service = GenService(
            domain_storage_engine=self._domain_storage_engine,
        )

        today = self._time_provider.get_current_date()

        for workspace in workspaces:
            progress_reporter = self._progress_reporter_factory.new_reporter(context)
            user = users_by_id[users_id_by_workspace_id[workspace.ref_id]]
            gen_targets = workspace.infer_sync_targets_for_enabled_features(None)

            await gen_service.do_it(
                ctx=ctx,
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

            async with self._search_storage_engine.get_unit_of_work() as search_uow:
                for created_entity in progress_reporter.created_entities:
                    await search_uow.search_repository.upsert(
                        workspace.ref_id, created_entity
                    )

                for updated_entity in progress_reporter.updated_entities:
                    await search_uow.search_repository.upsert(
                        workspace.ref_id, updated_entity
                    )

                for removed_entity in progress_reporter.removed_entities:
                    await search_uow.search_repository.remove(
                        workspace.ref_id, removed_entity
                    )
