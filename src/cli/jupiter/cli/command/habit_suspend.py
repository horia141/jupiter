"""UseCase for suspending of a habit."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.habits.suspend import HabitSuspendArgs, HabitSuspendUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class HabitSuspend(LoggedInMutationCommand[HabitSuspendUseCase]):
    """UseCase class for suspending a habit."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "habit-suspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Suspend a habit"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the habit to modify",
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
            HabitSuspendArgs(ref_id),
        )
