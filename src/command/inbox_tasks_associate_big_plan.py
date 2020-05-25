"""Command for associating an inbox task with a big plan."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksAssociateBigPlan(command.Command):
    """Command class for associating an inbox task with a big plan."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-associate-big-plan"

    @staticmethod
    def description():
        """The description of the command."""
        return "Associate an inbox task with a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")
        parser.add_argument("--big-plan-id", type=str, dest="big_plan_ref_id",
                            help="The id of a big plan to associate this task to.")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        big_plan_ref_id = self._basic_validator.entity_id_validate_and_clean(args.big_plan_ref_id)\
            if args.big_plan_ref_id else None
        self._inbox_tasks_controller.associate_inbox_task_with_big_plan(ref_id, big_plan_ref_id)
