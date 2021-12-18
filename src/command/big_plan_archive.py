"""Command for archiving a big plan."""
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from models.framework import EntityId
from use_cases.big_plans.archive import BigPlanArchiveCommand


class BigPlanArchive(command.Command):
    """Command class for archiving a big plan."""

    _command: Final[BigPlanArchiveCommand]

    def __init__(self, the_command: BigPlanArchiveCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(BigPlanArchiveCommand.Args(ref_id))
