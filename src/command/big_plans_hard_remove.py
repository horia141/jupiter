"""Command for hard remove big plans."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class BigPlansHardRemove(command.Command):
    """Command class for hard removing big plans."""

    _big_plans_controller: Final[BigPlansController]

    def __init__(self, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-hard-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove big plans"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        self._big_plans_controller.hard_remove_big_plans(ref_ids)
