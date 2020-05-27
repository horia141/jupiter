"""Command for updating big plans for a project."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.basic import BasicValidator, SyncPrefer

LOGGER = logging.getLogger(__name__)


class BigPlansSync(command.Command):
    """Command class for updating big plans for a project."""

    _basic_validator: Final[BasicValidator]
    _big_plans_controller: Final[BigPlansController]

    def __init__(self, basic_validator: BasicValidator, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-sync"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Upsert big plans"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True,
                            help="The key of the project")
        parser.add_argument("--prefer", dest="sync_prefer",
                            choices=BasicValidator.sync_prefer_values(), default=SyncPrefer.NOTION.value,
                            help="Which source to prefer")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project_key)
        sync_prefer = self._basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)
        self._big_plans_controller.big_plans_sync(project_key, sync_prefer)
