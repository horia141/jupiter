"""UseCase for hard removing habits."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.habits.remove import HabitRemoveArgs, HabitRemoveUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class HabitRemove(LoggedInMutationCommand[HabitRemoveUseCase]):
    """UseCase class for hard removing habits."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "habit-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove habits"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Show only tasks selected by this id",
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
            HabitRemoveArgs(ref_id),
        )
