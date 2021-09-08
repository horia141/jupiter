"""Command for archiving a big plan."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class BigPlansArchive(command.Command):
    """Command class for archiving a big plan."""

    _big_plans_controller: Final[BigPlansController]

    def __init__(self, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-archive"

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
        self._big_plans_controller.archive_big_plan(ref_id)
