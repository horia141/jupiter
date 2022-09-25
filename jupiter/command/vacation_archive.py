"""UseCase for removing a vacation."""

from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.vacations.archive import VacationArchiveUseCase


class VacationArchive(command.Command):
    """UseCase class for removing a vacation."""

    _command: Final[VacationArchiveUseCase]

    def __init__(self, the_command: VacationArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the vacations to remove",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(
            progress_reporter, VacationArchiveUseCase.Args(ref_id=ref_id)
        )
