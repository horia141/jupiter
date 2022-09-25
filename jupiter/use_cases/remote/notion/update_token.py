"""Usecase for updating a Notion connection token."""
from dataclasses import dataclass

from jupiter.domain.remote.notion.token import NotionToken
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, ProgressReporter
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)


class NotionConnectionUpdateTokenUseCase(
    AppMutationUseCase["NotionConnectionUpdateTokenUseCase.Args", None]
):
    """UseCase for updating a Notion connection token."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        token: NotionToken

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        with progress_reporter.start_updating_entity(
            "notion connection"
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                workspace = uow.workspace_repository.load()
                notion_connection = uow.notion_connection_repository.load_by_parent(
                    workspace.ref_id
                )
                entity_reporter.mark_known_entity_id(notion_connection.ref_id)
                notion_connection = notion_connection.update_token(
                    args.token, EventSource.CLI, self._time_provider.get_current_time()
                )
                uow.notion_connection_repository.save(notion_connection)
                entity_reporter.mark_local_change()
