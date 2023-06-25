"""UseCase for unsuspending of a chore."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.chores.unsuspend import (
    ChoreUnsuspendArgs,
    ChoreUnsuspendUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class ChoreUnsuspend(LoggedInMutationCommand[ChoreUnsuspendUseCase]):
    """UseCase class for unsuspending a chore."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-unsuspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Unsuspend a chore"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the chore to modify",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ChoreUnsuspendArgs(ref_id),
        )
