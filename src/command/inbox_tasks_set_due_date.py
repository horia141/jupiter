"""Command for setting the due date of an inbox task."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from domain.common.adate import ADate
from models.framework import EntityId
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class InboxTasksSetDueDate(command.Command):
    """Command class for setting the due date of an inbox task."""

    _global_properties: Final[GlobalProperties]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, global_properties: GlobalProperties, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-set-due-date"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Set the due date an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the inbox task")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the inbox task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        due_date = ADate.from_raw(self._global_properties.timezone, args.due_date) if args.due_date else None
        self._inbox_tasks_controller.set_inbox_task_due_date(ref_id, due_date)
