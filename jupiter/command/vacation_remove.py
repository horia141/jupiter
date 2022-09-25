"""UseCase for hard remove vacations."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.vacations.remove import VacationRemoveUseCase


class VacationRemove(command.Command):
    """UseCase class for hard removing vacations."""

    _command: Final[VacationRemoveUseCase]

    def __init__(self, the_command: VacationRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="Remove this vacation",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(
            progress_reporter, VacationRemoveUseCase.Args(ref_id=ref_id)
        )
