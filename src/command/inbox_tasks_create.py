"""Command for creating an inbox task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksCreate(command.Command):
    """Command class for creating inbox tasks."""

    _basic_validator: Final[BasicValidator]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, basic_validator: BasicValidator, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._inbox_tasks_controller = inbox_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-tasks-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=False,
                            help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the inbox task")
        parser.add_argument("--big-plan-id", type=str, dest="big_plan_ref_id",
                            help="The id of a big plan to associate this task to.")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=BasicValidator.eisen_values(), help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", choices=BasicValidator.difficulty_values(),
                            help="The difficulty to use for tasks")
        parser.add_argument("--actionable-date", dest="actionable_date", help="The active date of the inbox task")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project_key) \
            if args.project_key else None
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        big_plan_ref_id = self._basic_validator.entity_id_validate_and_clean(args.big_plan_ref_id) \
            if args.big_plan_ref_id else None
        eisen = [self._basic_validator.eisen_validate_and_clean(e) for e in args.eisen]
        difficulty = self._basic_validator.difficulty_validate_and_clean(args.difficulty) if args.difficulty else None
        actionable_date = self._basic_validator.adate_validate_and_clean(args.actionable_date) \
            if args.due_date else None
        due_date = self._basic_validator.adate_validate_and_clean(args.due_date) if args.due_date else None
        self._inbox_tasks_controller.create_inbox_task(
            project_key=project_key,
            name=name,
            big_plan_ref_id=big_plan_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date)
