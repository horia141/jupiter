"""Command for setting the must do status of a recurring task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetMustDo(command.Command):
    """Command class for setting the must do status of a recurring task."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-set-must-do"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the must do status of a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the recurring task to modify")
        parser.add_argument("--must-do", dest="must_do", default=False, action="store_true",
                            help="Whether to treat this task as must do or not")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        must_do = args.must_do
        self._recurring_tasks_controller.set_recurring_task_must_do_state(ref_id, must_do)
