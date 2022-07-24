"""Usecase for updating a Notion API access token."""
from dataclasses import dataclass

from jupiter.domain.remote.notion.api_token import NotionApiToken
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext


class NotionConnectionUpdateApiTokenUseCase(
    AppMutationUseCase["NotionConnectionUpdateApiTokenUseCase.Args", None]
):
    """UseCase for updating a Notion API access token."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        api_token: NotionApiToken

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            notion_connection = uow.notion_connection_repository.load_by_parent(
                workspace.ref_id
            )
            notion_connection = notion_connection.update_api_token(
                args.api_token, EventSource.CLI, self._time_provider.get_current_time()
            )
            uow.notion_connection_repository.save(notion_connection)
