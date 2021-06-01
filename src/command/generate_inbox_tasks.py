"""Command for creating recurring tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.generate_inbox_tasks import GenerateInboxTasksController
from models.framework import EntityId
from models.basic import BasicValidator, RecurringTaskPeriod, SyncTarget
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
        parser.add_argument("--target", dest="gen_targets", default=[], action="append",
                            choices=BasicValidator.sync_target_values(), help="What exactly to try to generate for")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--id", dest="recurring_task_ref_ids", default=[], action="append",
                            help="Allow only recurring tasks with this id")
        parser.add_argument("--metric", dest="metric_keys", default=[], action="append",
                            help="Allow only these metrics")
        parser.add_argument("--person", dest="person_ref_ids", default=[], action="append",
                            help="Allow only these persons")
        parser.add_argument("--period", default=[RecurringTaskPeriod.DAILY.value], action="append",
                            choices=BasicValidator.recurring_task_period_values(),
                            help="The period for which the upsert should happen. Defaults to all")
        parser.add_argument("--ignore-modified-times", dest="sync_even_if_not_modified", action="store_true",
                            default=False, help="Synchronise even if modification times would say otherwise")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        right_now = self._basic_validator.timestamp_validate_and_clean(args.date) \
            if args.date else self._time_provider.get_current_time()
        gen_targets = [self._basic_validator.sync_target_validate_and_clean(st) for st in args.gen_targets] \
            if len(args.gen_targets) > 0 else list(st for st in SyncTarget)
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys] \
            if len(args.project_keys) > 0 else None
        recurring_task_ref_ids = [
            EntityId.from_raw(rid) for rid in args.recurring_task_ref_ids] \
            if len(args.recurring_task_ref_ids) > 0 else None
        metric_keys = [self._basic_validator.metric_key_validate_and_clean(mk) for mk in args.metric_keys] \
            if len(args.metric_keys) > 0 else None
        person_ref_ids = [
            EntityId.from_raw(rid) for rid in args.person_ref_ids] \
            if len(args.person_ref_ids) > 0 else None
        period_filter = frozenset(self._basic_validator.recurring_task_period_validate_and_clean(p)
                                  for p in args.period) \
            if len(args.period) > 0 else None
        sync_even_if_not_modified: bool = args.sync_even_if_not_modified
        self._generate_inbox_tasks_controller.recurring_tasks_gen(
            right_now, gen_targets, project_keys, recurring_task_ref_ids, metric_keys, person_ref_ids, period_filter,
            sync_even_if_not_modified)
