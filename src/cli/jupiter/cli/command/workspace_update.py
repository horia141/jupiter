"""UseCase for updating the workspace."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.workspaces.update import (
    WorkspaceUpdateArgs,
    WorkspaceUpdateUseCase,
)


class WorkspaceUpdate(LoggedInMutationCommand[WorkspaceUpdateUseCase]):
    """UseCase class for updating the workspace."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", required=False, help="The workspace name to use")

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        if args.name is not None:
            name = UpdateAction.change_to(WorkspaceName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.timezone is not None:
            UpdateAction.change_to(Timezone.from_raw(args.timezone))
        else:
            UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            WorkspaceUpdateArgs(name=name),
        )
