"""Command for creating recurring tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks_gen import RecurringTasksGenController
from models.basic import BasicValidator
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTasksGen(command.Command):
    """Command class for creating recurring tasks."""

    _basic_validator: Final[BasicValidator]
    _time_provider: Final[TimeProvider]
    _recurring_tasks_gen_controller: Final[RecurringTasksGenController]

    def __init__(
            self, basic_validator: BasicValidator, time_provider: TimeProvider,
            recurring_tasks_gen_controller: RecurringTasksGenController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._time_provider = time_provider
        self._recurring_tasks_gen_controller = recurring_tasks_gen_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "gen"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create recurring tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--date", help="The date on which the upsert should run at")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--group", default=[], action="append",
                            help="The groups for which the upsert should happen. Defaults to all")
        parser.add_argument("--period", default=[], action="append",
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period for which the upsert should happen. Defaults to all")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        right_now = self._basic_validator.datetime_validate_and_clean(args.date) \
            if args.date else self._time_provider.get_current_time()
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys] \
            if len(args.project_keys) > 0 else None
        group_filter = [self._basic_validator.entity_name_validate_and_clean(g) for g in args.group] \
            if len(args.group) > 0 else None
        period_filter = [self._basic_validator.recurring_task_period_validate_and_clean(p) for p in args.period] \
            if len(args.period) > 0 else None
        self._recurring_tasks_gen_controller.recurring_tasks_gen(right_now, project_keys, group_filter, period_filter)
