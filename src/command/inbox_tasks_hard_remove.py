"""Command for hard remove inbox tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class InboxTasksHardRemove(command.Command):
    """Command class for hard removing inbox tasks."""

    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-hard-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove inbox tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        self._inbox_tasks_controller.hard_remove_inbox_tasks(ref_ids)
