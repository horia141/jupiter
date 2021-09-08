"""Command for setting the difficulty of an inbox task."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from domain.common.difficulty import Difficulty
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class InboxTasksSetDifficulty(command.Command):
    """Command class for setting the difficulty of an inbox task."""

    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-set-difficulty"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Set the difficulty an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")
        parser.add_argument("--difficulty", dest="difficulty", choices=Difficulty.all_values(),
                            help="The difficulty to use for tasks")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        difficulty = Difficulty.from_raw(args.difficulty) if args.difficulty else None
        self._inbox_tasks_controller.set_inbox_task_difficulty(ref_id, difficulty)
