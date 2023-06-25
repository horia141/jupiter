"""UseCase for hard remove slack tasks."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.push_integrations.slack.remove import (
    SlackTaskRemoveArgs,
    SlackTaskRemoveUseCase,
)


class SlackTaskRemove(LoggedInMutationCommand[SlackTaskRemoveUseCase]):
    """UseCase class for hard removing slack tasks."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove slack tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Remove this Slack task",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SlackTaskRemoveArgs(ref_id),
        )
