"""Command for creating recurring tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.generate_inbox_tasks import GenerateInboxTasksController
from models.basic import BasicValidator, RecurringTaskPeriod
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class GenerateInboxTasks(command.Command):
    """Command class for creating recurring tasks."""

    _basic_validator: Final[BasicValidator]
    _time_provider: Final[TimeProvider]
    _generate_inbox_tasks_controller: Final[GenerateInboxTasksController]

    def __init__(
            self, basic_validator: BasicValidator, time_provider: TimeProvider,
            generate_inbox_tasks_controller: GenerateInboxTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._time_provider = time_provider
        self._generate_inbox_tasks_controller = generate_inbox_tasks_controller

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
        parser.add_argument("--id", dest="ref_ids", default=[], action="append",
                            help="Allow only tasks with this id")
        parser.add_argument("--period", default=[RecurringTaskPeriod.DAILY.value], action="append",
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period for which the upsert should happen. Defaults to all")
        parser.add_argument("--ignore-modified-times", dest="sync_even_if_not_modified", action="store_true",
                            default=False, help="Drop all Notion-side archived")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        right_now = self._basic_validator.timestamp_validate_and_clean(args.date) \
            if args.date else self._time_provider.get_current_time()
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys] \
            if len(args.project_keys) > 0 else None
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        period_filter = frozenset(self._basic_validator.recurring_task_period_validate_and_clean(p)
                                  for p in args.period) \
            if len(args.period) > 0 else None
        sync_even_if_not_modified: bool = args.sync_even_if_not_modified
        self._generate_inbox_tasks_controller.recurring_tasks_gen(
            right_now, project_keys, ref_ids, period_filter, sync_even_if_not_modified)
