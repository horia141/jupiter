"""Command for setting the name of a big plan."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class BigPlansSetName(command.Command):
    """Command class for setting the name of a big plan."""

    _basic_validator: Final[BasicValidator]
    _big_plans_controller: Final[BigPlansController]

    def __init__(self, basic_validator: BasicValidator, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-set-name"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the name of a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--name", dest="name", required=True, help="The name of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        self._big_plans_controller.set_big_plan_name(ref_id, name)
