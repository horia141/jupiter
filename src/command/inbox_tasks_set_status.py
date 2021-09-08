"""Command for setting the status of an inbox task."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class InboxTasksSetStatus(command.Command):
    """Command class for setting the status of an inbox task."""

    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
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
        parser.add_argument("--status", dest="status", required=True, choices=InboxTaskStatus.all_values(),
                            help="The status of the inbox task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        status = InboxTaskStatus.from_raw(args.status)
        self._inbox_tasks_controller.set_inbox_task_status(ref_id, status)
