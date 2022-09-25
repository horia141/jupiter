"""UseCase for suspending of a habit."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.habits.suspend import HabitSuspendUseCase


class HabitSuspend(command.Command):
    """UseCase class for suspending a habit."""

    _command: Final[HabitSuspendUseCase]

    def __init__(self, the_command: HabitSuspendUseCase) -> None:
        """Constructor."""
        self._command = the_command

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

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, HabitSuspendUseCase.Args(ref_id))
