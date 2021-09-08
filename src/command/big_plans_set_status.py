"""Command for setting the status of a big plan."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from domain.big_plans.big_plan_status import BigPlanStatus
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class BigPlansSetStatus(command.Command):
    """Command class for setting the status of a big plan."""

    _big_plans_controller: Final[BigPlansController]

    def __init__(self, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-set-status"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the status of a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--status", dest="status", required=True,
                            choices=BigPlanStatus.all_values(), help="The status of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        status = BigPlanStatus.from_raw(args.status)
        self._big_plans_controller.set_big_plan_status(ref_id, status)
