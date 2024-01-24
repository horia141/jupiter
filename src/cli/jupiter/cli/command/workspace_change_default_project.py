"""UseCase for changing the default project the workspace."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectArgs,
    WorkspaceChangeDefaultProjectUseCase,
)


class WorkspaceChangeDefaultProject(
    LoggedInMutationCommand[WorkspaceChangeDefaultProjectUseCase]
):
    """UseCase class for changing the default project of the workspace."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--default-project-id",
            dest="default_project_ref_id",
            required=True,
            help="The key of the default project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        default_project_ref_id = EntityId.from_raw(args.default_project_ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            WorkspaceChangeDefaultProjectArgs(
                default_project_ref_id=default_project_ref_id
            ),
        )
