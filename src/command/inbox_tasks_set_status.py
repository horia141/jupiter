"""Command for setting the status of an inbox task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksSetStatus(command.Command):
    """Command class for setting the status of an inbox task."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-set-status"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Set the status an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")
        parser.add_argument("--status", dest="status", required=True, choices=BasicValidator.inbox_task_status_values(),
                            help="The status of the inbox task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        status = self._basic_validator.inbox_task_status_validate_and_clean(args.status)
        self._inbox_tasks_controller.set_inbox_task_status(ref_id, status)
