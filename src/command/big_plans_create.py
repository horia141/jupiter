"""Command for creating big plans."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class BigPlansCreate(command.Command):
    """Command class for creating big plans."""

    _basic_validator: Final[BasicValidator]
    _big_plans_controller: Final[BigPlansController]

    def __init__(self, basic_validator: BasicValidator, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project", required=True,
                            help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the big plan")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        due_date = self._basic_validator.date_validate_and_clean(args.due_date) if args.due_date else None
        self._big_plans_controller.create_big_plan(project_key, name, due_date)
