"""Command for removing a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from use_cases.vacations.archive import VacationArchiveCommand
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class VacationArchive(command.Command):
    """Command class for removing a vacation."""

    _command: Final[VacationArchiveCommand]

    def __init__(self, the_command: VacationArchiveCommand) -> None:
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
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the vacations to remove")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(ref_id)
