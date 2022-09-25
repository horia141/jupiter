"""UseCase for unsuspending of a habit."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.habits.unsuspend import HabitUnsuspendUseCase


class HabitUnsuspend(command.Command):
    """UseCase class for unsuspending a habit."""

    _command: Final[HabitUnsuspendUseCase]

    def __init__(self, the_command: HabitUnsuspendUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "habit-unsuspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Unsuspend a habit"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the habit to modify",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, HabitUnsuspendUseCase.Args(ref_id))
