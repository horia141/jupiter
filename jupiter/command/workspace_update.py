"""UseCase for updating the workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import jupiter.command.command as command
from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.notion_token import NotionToken
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.update_action import UpdateAction
from jupiter.remote.notion.infra.connection import NotionConnection
from jupiter.use_cases.workspaces.update import WorkspaceUpdateUseCase

LOGGER = logging.getLogger(__name__)


class WorkspaceUpdate(command.Command):
    """UseCase class for updating the workspace."""

    _notion_connection: Final[NotionConnection]
    _command: Final[WorkspaceUpdateUseCase]

    def __init__(self, notion_connection: NotionConnection, the_command: WorkspaceUpdateUseCase) -> None:
        """Constructor."""
        self._notion_connection = notion_connection
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--name", required=False, help="The plan name to use")
        parser.add_argument(
            "--timezone", required=False, help="The timezone you're currently in")
        parser.add_argument("--notion-token", dest="notion_token", required=False, help="The Notion token")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        if args.name is not None:
            name = UpdateAction.change_to(WorkspaceName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.timezone is not None:
            timezone = UpdateAction.change_to(Timezone.from_raw(args.timezone))
        else:
            timezone = UpdateAction.do_nothing()
        # This is quite the hack for now!
        if args.notion_token is not None:
            self._notion_connection.update_token(NotionToken.from_raw(args.notion_token))
        self._command.execute(WorkspaceUpdateUseCase.Args(name=name, timezone=timezone))
