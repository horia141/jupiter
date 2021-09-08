"""Command for creating an inbox task."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.inbox_tasks import InboxTasksController
from domain.common.adate import ADate
from domain.common.difficulty import Difficulty
from domain.common.eisen import Eisen
from domain.common.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from models.framework import EntityId
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class InboxTasksCreate(command.Command):
    """Command class for creating inbox tasks."""

    _global_properties: Final[GlobalProperties]
    _inbox_tasks_controller: Final[InboxTasksController]

    def __init__(self, global_properties: GlobalProperties, inbox_tasks_controller: InboxTasksController) -> None:
        """Constructor."""
        self._global_properties = global_properties
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
                            choices=Eisen.all_values(), help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", choices=Difficulty.all_values(),
                            help="The difficulty to use for tasks")
        parser.add_argument("--actionable-date", dest="actionable_date", help="The active date of the inbox task")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = ProjectKey.from_raw(args.project_key) if args.project_key else None
        name = EntityName.from_raw(args.name)
        big_plan_ref_id = EntityId.from_raw(args.big_plan_ref_id) \
            if args.big_plan_ref_id else None
        eisen = [Eisen.from_raw(e) for e in args.eisen]
        difficulty = Difficulty.from_raw(args.difficulty) if args.difficulty else None
        actionable_date = ADate.from_raw(self._global_properties.timezone, args.actionable_date) \
            if args.due_date else None
        due_date = ADate.from_raw(self._global_properties.timezone, args.due_date) if args.due_date else None
        self._inbox_tasks_controller.create_inbox_task(
            project_key=project_key,
            name=name,
            big_plan_ref_id=big_plan_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date)
