"""UseCase for generating reports of progress."""
from argparse import ArgumentParser, Namespace
from typing import Final

from command import command
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.metrics.metric_key import MetricKey
from domain.projects.project_key import ProjectKey
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_type import RecurringTaskType
from framework.base.timestamp import Timestamp
from framework.errors import ModelValidationError
from framework.base.entity_id import EntityId
from use_cases.report import ReportUseCase
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider


class Report(command.Command):
    """UseCase class for reporting progress."""

    _SOURCES_TO_REPORT = [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.RECURRING_TASK,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.PERSON_BIRTHDAY
    ]

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _command: Final[ReportUseCase]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            the_command: ReportUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "report"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Report on progress"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--date", help="The date on which the upsert should run at")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--source", dest="sources", default=[], action="append",
                            choices=InboxTaskSource.all_values(),
                            help="Allow only inbox tasks form this particular source. Defaults to all")
        parser.add_argument("--big-plan-id", dest="big_plan_ref_ids", default=[], action="append",
                            help="Allow only tasks from these big plans")
        parser.add_argument("--recurring-task-id", dest="recurring_task_ref_ids", default=[], action="append",
                            help="Allow only tasks from these recurring tasks")
        parser.add_argument("--metric", dest="metric_keys", required=False, default=[], action="append",
                            help="The key of the metric")
        parser.add_argument("--person-id", dest="person_ref_ids", default=[], action="append",
                            help="Allow only tasks from these persons")
        parser.add_argument("--cover", dest="covers", default=["inbox-tasks", "big-plans"],
                            choices=["inbox-tasks", "big-plans"],
                            help="Show reporting info about certain parts")
        parser.add_argument("--breakdown", dest="breakdowns", default=[], action="append",
                            choices=["global", "projects", "periods", "big-plans", "recurring-tasks", "metrics"],
                            help="Breakdown report by one or more dimensions")
        parser.add_argument("--sub-period", dest="breakdown_period", default=None,
                            choices=RecurringTaskPeriod.all_values(),
                            help="Specify subperiod to use when breaking down by period")
        parser.add_argument("--recurring-task-type", dest="recurring_task_types", default=[], action="append",
                            choices=RecurringTaskType.all_values(),
                            help="Allow only recurring tasks of this type")
        parser.add_argument("--period", default=RecurringTaskPeriod.WEEKLY.value, dest="period",
                            choices=RecurringTaskPeriod.all_values(),
                            help="The period to report on")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        right_now = Timestamp.from_raw(self._global_properties.timezone, args.date) \
            if args.date else self._time_provider.get_current_time()
        project_keys = [ProjectKey.from_raw(pk) for pk in args.project_keys] if len(args.project_keys) > 0 else None
        sources = [InboxTaskSource.from_raw(s) for s in args.sources] \
            if len(args.sources) > 0 else None
        big_plan_ref_ids = [EntityId.from_raw(bp) for bp in args.big_plan_ref_ids] \
            if len(args.big_plan_ref_ids) > 0 else None
        recurring_task_ref_ids = [EntityId.from_raw(rt)
                                  for rt in args.recurring_task_ref_ids] \
            if len(args.recurring_task_ref_ids) > 0 else None
        metric_keys = [MetricKey.from_raw(mk) for mk in args.metric_keys] \
            if len(args.metric_keys) > 0 else None
        person_ref_ids = [EntityId.from_raw(bp) for bp in args.person_ref_ids] \
            if len(args.person_ref_ids) > 0 else None
        covers = args.covers
        breakdowns = args.breakdowns if len(args.breakdowns) > 0 else ["global"]
        breakdown_period_raw = RecurringTaskPeriod.from_raw(args.breakdown_period) \
            if args.breakdown_period else None
        recurring_task_types = [RecurringTaskType.from_raw(rtt)
                                for rtt in args.recurring_task_types] \
            if len(args.recurring_task_types) > 0 else list(rtt for rtt in RecurringTaskType)
        period = RecurringTaskPeriod.from_raw(args.period)

        breakdown_period = None
        if "periods" in breakdowns:
            if breakdown_period_raw is None:
                breakdown_period = self._one_smaller_than_period(period)
            else:
                breakdown_period = self._check_period_against_breakdown_period(breakdown_period_raw, period)

        response = self._command.execute(ReportUseCase.Args(
            right_now=right_now,
            filter_project_keys=project_keys,
            filter_sources=sources,
            filter_big_plan_ref_ids=big_plan_ref_ids,
            filter_recurring_task_ref_ids=recurring_task_ref_ids,
            filter_metric_keys=metric_keys,
            filter_person_ref_ids=person_ref_ids,
            period=period,
            breakdown_period=breakdown_period))

        sources_to_present = [s for s in Report._SOURCES_TO_REPORT if s in sources]\
            if sources else Report._SOURCES_TO_REPORT

        print(f"{period.for_notion()} as of {right_now}:")

        if "global" in breakdowns:
            print(f"  Global:")

            if "inbox-tasks" in covers:
                print(f"    Inbox Tasks:")
                print(f"      Created: {response.global_inbox_tasks_summary.created.total_cnt}", end=" ")
                for source in sources_to_present:
                    print(f"({response.global_inbox_tasks_summary.created.per_source_cnt[source]} " +
                          f"from {source.for_notion()})", end=" ")
                print("")
                print(f"      Accepted: {response.global_inbox_tasks_summary.accepted.total_cnt}", end=" ")
                for source in sources_to_present:
                    print(f"({response.global_inbox_tasks_summary.accepted.per_source_cnt[source]} " +
                          f"from {source.for_notion()})", end=" ")
                print("")
                print(f"      Working: {response.global_inbox_tasks_summary.working.total_cnt}", end=" ")
                for source in sources_to_present:
                    print(f"({response.global_inbox_tasks_summary.working.per_source_cnt[source]} " +
                          f"from {source.for_notion()})", end=" ")
                print("")
                print(f"      Not Done: {response.global_inbox_tasks_summary.not_done.total_cnt}", end=" ")
                for source in sources_to_present:
                    print(f"({response.global_inbox_tasks_summary.not_done.per_source_cnt[source]} " +
                          f"from {source.for_notion()})", end=" ")
                print("")
                print(f"      Done: {response.global_inbox_tasks_summary.done.total_cnt}", end=" ")
                for source in sources_to_present:
                    print(f"({response.global_inbox_tasks_summary.done.per_source_cnt[source]} " +
                          f"from {source.for_notion()})", end=" ")
                print("")

            if "big-plans" in covers:
                print(f"    Big Plans:")
                print(f"      Created: {response.global_big_plans_summary.created_cnt}")
                print(f"      Accepted: {response.global_big_plans_summary.accepted_cnt}")
                print(f"      Working: {response.global_big_plans_summary.working_cnt}")
                print(f"      Not Done: {response.global_big_plans_summary.not_done_cnt}")
                for big_plan_name in response.global_big_plans_summary.not_done_projects:
                    print(f"      - {big_plan_name}")
                print(f"      Done: {response.global_big_plans_summary.done_cnt}")
                for big_plan_name in response.global_big_plans_summary.done_projects:
                    print(f"      - {big_plan_name}")

        if "projects" in breakdowns:
            print(f"  By Project:")

            for project_item in response.per_project_breakdown:
                print(f"    {project_item.name}:")
                if "inbox-tasks" in covers:
                    print(f"      Inbox Tasks:")
                    print(f"        Created: {project_item.inbox_tasks_summary.created.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({project_item.inbox_tasks_summary.created.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Accepted: {project_item.inbox_tasks_summary.accepted.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({project_item.inbox_tasks_summary.accepted.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Working: {project_item.inbox_tasks_summary.working.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({project_item.inbox_tasks_summary.working.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Not Done: {project_item.inbox_tasks_summary.not_done.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({project_item.inbox_tasks_summary.not_done.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Done: {project_item.inbox_tasks_summary.done.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({project_item.inbox_tasks_summary.done.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")

                if "big-plans" in covers:
                    print(f"      Big Plans:")
                    print(f"        Created: {project_item.big_plans_summary.created_cnt}")
                    print(f"        Accepted: {project_item.big_plans_summary.accepted_cnt}")
                    print(f"        Working: {project_item.big_plans_summary.working_cnt}")
                    print(f"        Not Done: {project_item.big_plans_summary.not_done_cnt}")
                    for big_plan_name in project_item.big_plans_summary.not_done_projects:
                        print(f"        - {big_plan_name}")
                    print(f"        Done: {project_item.big_plans_summary.done_cnt}")
                    for big_plan_name in project_item.big_plans_summary.done_projects:
                        print(f"        - {big_plan_name}")

        if "periods" in breakdowns:
            print(f"  By Period:")

            if not response.per_period_breakdown:
                raise Exception("Did not find any per period breakdown even if it's asked for")

            for period_item in response.per_period_breakdown:
                print(f"    {period_item.name}:")
                if "inbox-tasks" in covers:
                    print(f"      Inbox Tasks:")
                    print(f"        Created: {period_item.inbox_tasks_summary.created.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({period_item.inbox_tasks_summary.created.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Accepted: {period_item.inbox_tasks_summary.accepted.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({period_item.inbox_tasks_summary.accepted.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Working: {period_item.inbox_tasks_summary.working.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({period_item.inbox_tasks_summary.working.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Not Done: {period_item.inbox_tasks_summary.not_done.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({period_item.inbox_tasks_summary.not_done.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")
                    print(f"        Done: {period_item.inbox_tasks_summary.done.total_cnt}", end=" ")
                    for source in sources_to_present:
                        print(f"({period_item.inbox_tasks_summary.done.per_source_cnt[source]} " +
                              f"from {source.for_notion()})", end=" ")
                    print("")

                if "big-plans" in covers:
                    print(f"      Big Plans:")
                    print(f"        Created: {period_item.big_plans_summary.created_cnt}")
                    print(f"        Accepted: {period_item.big_plans_summary.accepted_cnt}")
                    print(f"        Working: {period_item.big_plans_summary.working_cnt}")
                    print(f"        Not Done: {period_item.big_plans_summary.not_done_cnt}")
                    for big_plan_name in period_item.big_plans_summary.not_done_projects:
                        print(f"        - {big_plan_name}")
                    print(f"        Done: {period_item.big_plans_summary.done_cnt}")
                    for big_plan_name in period_item.big_plans_summary.done_projects:
                        print(f"        - {big_plan_name}")

        if "big-plans" in breakdowns:
            print(f"  By Big Plan:")

            for big_plan_item in response.per_big_plan_breakdown:
                print(f"    {big_plan_item.name}:")
                print(f"      Created: {big_plan_item.summary.created_cnt}")
                print(f"      Accepted: {big_plan_item.summary.accepted_cnt}")
                print(f"      Working: {big_plan_item.summary.working_cnt}")
                print(f"      Not Done: {big_plan_item.summary.not_done_cnt}", end=" ")
                print(f"({big_plan_item.summary.not_done_ratio * 100:.0f}%)")
                print(f"      Done: {big_plan_item.summary.done_cnt}", end=" ")
                print(f"({big_plan_item.summary.done_ratio * 100:.0f}%)")
                print(f"      Completed Ratio: {big_plan_item.summary.completed_ratio * 100:.0f}%")

        if "recurring-tasks" in breakdowns:
            print(f"  By Recurring Task:")

            for recurring_task_item in response.per_recurring_task_breakdown:
                if recurring_task_item.the_type not in recurring_task_types:
                    continue

                print(f"    {recurring_task_item.name}:")
                print(f"      Created: {recurring_task_item.summary.created_cnt}")
                print(f"      In Progress: {recurring_task_item.summary.accepted_cnt}")
                print(f"      Working: {recurring_task_item.summary.working_cnt}")
                print(f"      Not Done: {recurring_task_item.summary.not_done_cnt}", end=" ")
                print(f"({recurring_task_item.summary.not_done_ratio * 100:.0f}%)")
                print(f"      Done: {recurring_task_item.summary.done_cnt}", end=" ")
                print(f"({recurring_task_item.summary.done_ratio * 100:.0f}%)")
                if recurring_task_item.the_type == RecurringTaskType.HABIT:
                    print(f"      Completed Ratio: {recurring_task_item.summary.completed_ratio * 100:.0f}%")
                    print(f"      Current Streak: {recurring_task_item.summary.current_streak_size}")
                    print(f"      Longest Streak: {recurring_task_item.summary.longest_streak_size}")
                    if recurring_task_item.summary.one_streak_size_histogram:
                        print(f"      Streak Sizes (Max 1 Skip):")
                        for streak_size in sorted(recurring_task_item.summary.one_streak_size_histogram.keys()):
                            print(f"        {streak_size} =>", end=" ")
                            print(f"{recurring_task_item.summary.one_streak_size_histogram[streak_size]}")
                    print(f"      Avg Done:")
                    print(f"        Overall: {recurring_task_item.summary.avg_done_total * 100:2.1f}%")
                    for bigger_period, bigger_result in recurring_task_item.summary.avg_done_last_period.items():
                        print(f"        {bigger_period.for_notion()}: {bigger_result * 100:2.1f}%")
                    print(f"      Streak Plot: {recurring_task_item.summary.streak_plot}")

    @staticmethod
    def _one_smaller_than_period(period: RecurringTaskPeriod) -> RecurringTaskPeriod:
        if period == RecurringTaskPeriod.YEARLY:
            return RecurringTaskPeriod.QUARTERLY
        elif period == RecurringTaskPeriod.QUARTERLY:
            return RecurringTaskPeriod.MONTHLY
        elif period == RecurringTaskPeriod.MONTHLY:
            return RecurringTaskPeriod.WEEKLY
        elif period == RecurringTaskPeriod.WEEKLY:
            return RecurringTaskPeriod.DAILY
        else:
            raise ModelValidationError("Cannot breakdown daily by period")

    @staticmethod
    def _check_period_against_breakdown_period(
            breakdown_period: RecurringTaskPeriod, period: RecurringTaskPeriod) -> RecurringTaskPeriod:
        breakdown_period_idx = [v.value for v in RecurringTaskPeriod].index(breakdown_period.value)
        period_idx = [v.value for v in RecurringTaskPeriod].index(period.value)
        if breakdown_period_idx >= period_idx:
            raise ModelValidationError(f"Cannot breakdown {period.for_notion()} with {breakdown_period.for_notion()}")
        return breakdown_period
