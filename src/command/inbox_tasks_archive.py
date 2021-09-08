"""Command for archiving an inbox task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class InboxTasksArchive(command.Command):
    """Command class for archiving an inbox task."""

    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._inbox_tasks_controller.archive_inbox_task(ref_id)
