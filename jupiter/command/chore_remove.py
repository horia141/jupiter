"""UseCase for hard removing chores."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.chores.remove import ChoreRemoveUseCase


class ChoreRemove(command.Command):
    """UseCase class for hard removing chores."""

    _command: Final[ChoreRemoveUseCase]

    def __init__(self, the_command: ChoreRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove chores"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Show only tasks selected by this id",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, ChoreRemoveUseCase.Args(ref_id))
