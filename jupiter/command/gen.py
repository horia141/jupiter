"""UseCase for creating recurring tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.sync_target import SyncTarget
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.use_cases.gen import GenUseCase
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class Gen(command.Command):
    """UseCase class for creating recurring tasks."""

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _command: Final[GenUseCase]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            the_command: GenUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._command = the_command

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
                            choices=SyncTarget.all_values(), help="What exactly to try to generate for")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--habit-id", dest="habit_ref_ids", default=[], action="append",
                            help="Allow only habits with this id")
        parser.add_argument("--chore-id", dest="chore_ref_ids", default=[], action="append",
                            help="Allow only chores with this id")
        parser.add_argument("--metric", dest="metric_keys", default=[], action="append",
                            help="Allow only these metrics")
        parser.add_argument("--person", dest="person_ref_ids", default=[], action="append",
                            help="Allow only these persons")
        parser.add_argument("--slack-task-id", dest="slack_task_ref_ids", default=[], action="append",
                            help="Allow only these Slack tasks")
        parser.add_argument("--period", default=[RecurringTaskPeriod.DAILY.value], action="append",
                            choices=RecurringTaskPeriod.all_values(),
                            help="The period for which the upsert should happen. Defaults to all")
        parser.add_argument("--ignore-modified-times", dest="sync_even_if_not_modified", action="store_true",
                            default=False, help="Synchronise even if modification times would say otherwise")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        right_now = Timestamp.from_raw(self._global_properties.timezone, args.date) \
            if args.date else self._time_provider.get_current_time()
        gen_targets = [SyncTarget.from_raw(st) for st in args.gen_targets] \
            if len(args.gen_targets) > 0 else list(st for st in SyncTarget)
        project_keys = [ProjectKey.from_raw(pk) for pk in args.project_keys] if len(args.project_keys) > 0 else None
        habit_ref_ids = [EntityId.from_raw(rid) for rid in args.habit_ref_ids] if len(args.habit_ref_ids) > 0 else None
        chore_ref_ids = [EntityId.from_raw(rid) for rid in args.chore_ref_ids] if len(args.chore_ref_ids) > 0 else None
        metric_keys = [MetricKey.from_raw(mk) for mk in args.metric_keys] if len(args.metric_keys) > 0 else None
        person_ref_ids = \
            [EntityId.from_raw(rid) for rid in args.person_ref_ids] if len(args.person_ref_ids) > 0 else None
        slack_task_ref_ids = \
            [EntityId.from_raw(rid) for rid in args.slack_task_ref_ids] if len(args.slack_task_ref_ids) > 0 else None
        period_filter = \
            frozenset(RecurringTaskPeriod.from_raw(p) for p in args.period) if len(args.period) > 0 else None
        sync_even_if_not_modified: bool = args.sync_even_if_not_modified
        self._command.execute(GenUseCase.Args(
            right_now=right_now,
            gen_targets=gen_targets,
            filter_project_keys=project_keys,
            filter_habit_ref_ids=habit_ref_ids,
            filter_chore_ref_ids=chore_ref_ids,
            filter_metric_keys=metric_keys,
            filter_person_ref_ids=person_ref_ids,
            filter_slack_task_ref_ids=slack_task_ref_ids,
            filter_period=period_filter,
            sync_even_if_not_modified=sync_even_if_not_modified))
