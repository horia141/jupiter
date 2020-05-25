"""Command for setting the name of an inbox task."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksSetName(command.Command):
    """Command class for setting the name of an inbox task."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-set-name"

    @staticmethod
    def description():
        """The description of the command."""
        return "Set the name an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the inbox task")
        parser.add_argument("--name", dest="name", required=True, help="The name of the inbox task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        self._inbox_tasks_controller.set_inbox_task_name(ref_id, name)
