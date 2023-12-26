"""The command for reporting on progress."""
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import groupby
from operator import itemgetter
from typing import DefaultDict, Dict, Iterable, List, Optional, cast

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.schedules import Schedule
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    UserFeature,
    WorkspaceFeature,
)
from jupiter.core.domain.gamification.service.score_overview_service import (
    ScoreOverviewService,
)
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)


@dataclass
class ReportArgs(UseCaseArgsBase):
    """Report args."""

    today: ADate
    period: RecurringTaskPeriod
    filter_sources: Optional[Iterable[InboxTaskSource]] = None
    filter_project_ref_ids: Optional[Iterable[EntityId]] = None
    filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None
    filter_habit_ref_ids: Optional[Iterable[EntityId]] = None
    filter_chore_ref_ids: Optional[Iterable[EntityId]] = None
    filter_metric_ref_ids: Optional[Iterable[EntityId]] = None
    filter_person_ref_ids: Optional[Iterable[EntityId]] = None
    filter_slack_task_ref_ids: Optional[Iterable[EntityId]] = None
    filter_email_task_ref_ids: Optional[Iterable[EntityId]] = None
    breakdown_period: Optional[RecurringTaskPeriod] = None


@dataclass
class NestedResultPerSource:
    """A particular result broken down by the various sources of inbox tasks."""

    source: InboxTaskSource
    count: int


@dataclass
class NestedResult:
    """A result broken down by the various sources of inbox tasks."""

    total_cnt: int
    per_source_cnt: List[NestedResultPerSource]


@dataclass
class InboxTasksSummary:
    """A bigger summary for inbox tasks."""

    created: NestedResult
    accepted: NestedResult
    working: NestedResult
    not_done: NestedResult
    done: NestedResult


@dataclass
class WorkableBigPlan:
    """The view of a big plan via a workable."""

    ref_id: EntityId
    name: BigPlanName
    actionable_date: Optional[ADate] = None


@dataclass
class WorkableSummary:
    """The reporting summary."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    done_cnt: int
    not_done_big_plans: List[WorkableBigPlan]
    done_big_plans: List[WorkableBigPlan]


@dataclass
class BigPlanWorkSummary:
    """The report for a big plan."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float


@dataclass
class RecurringTaskWorkSummary:
    """The reporting summary."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float
    streak_plot: str = field(hash=False, compare=False, repr=False, default="")


@dataclass
class PerProjectBreakdownItem:
    """The report for a particular project."""

    ref_id: EntityId
    name: EntityName
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@dataclass
class PerPeriodBreakdownItem:
    """The report for a particular time period."""

    name: EntityName
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@dataclass
class PerBigPlanBreakdownItem:
    """The report for a particular big plan."""

    ref_id: EntityId
    name: EntityName
    actionable_date: Optional[ADate]
    summary: BigPlanWorkSummary


@dataclass
class PerHabitBreakdownItem:
    """The report for a particular habit."""

    ref_id: EntityId
    name: EntityName
    archived: bool
    period: RecurringTaskPeriod
    suspended: bool
    summary: RecurringTaskWorkSummary


@dataclass
class PerChoreBreakdownItem:
    """The report for a particular chore."""

    ref_id: EntityId
    name: EntityName
    suspended: bool
    archived: bool
    period: RecurringTaskPeriod
    summary: RecurringTaskWorkSummary


@dataclass
class ReportResult(UseCaseResultBase):
    """Report result."""

    today: ADate
    period: RecurringTaskPeriod
    global_inbox_tasks_summary: InboxTasksSummary
    global_big_plans_summary: WorkableSummary
    per_project_breakdown: List[PerProjectBreakdownItem]
    per_period_breakdown: List[PerPeriodBreakdownItem]
    per_habit_breakdown: List[PerHabitBreakdownItem]
    per_chore_breakdown: List[PerChoreBreakdownItem]
    per_big_plan_breakdown: List[PerBigPlanBreakdownItem]
    user_score_overview: UserScoreOverview | None


@readonly_use_case()
class ReportUseCase(AppLoggedInReadonlyUseCase[ReportArgs, ReportResult]):
    """The command for reporting on progress."""

    async def _execute(
        self,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ReportArgs,
    ) -> ReportResult:
        """Execute the command."""
        user = context.user
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.HABITS)
            and args.filter_habit_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.HABITS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.CHORES)
            and args.filter_chore_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.CHORES)
        if (
            not workspace.is_feature_available(WorkspaceFeature.METRICS)
            and args.filter_metric_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.METRICS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.PERSONS)
            and args.filter_person_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PERSONS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.SLACK_TASKS)
            and args.filter_slack_task_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.SLACK_TASKS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.EMAIL_TASKS)
            and args.filter_email_task_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.EMAIL_TASKS)

        filter_sources = (
            args.filter_sources
            if args.filter_sources is not None
            else workspace.infer_sources_for_enabled_features(None)
        )

        big_diff = list(
            set(filter_sources).difference(
                workspace.infer_sources_for_enabled_features(filter_sources)
            )
        )
        if len(big_diff) > 0:
            raise FeatureUnavailableError(
                f"Sources {','.join(s.value for s in big_diff)} are not supported in this workspace"
            )

        if args.breakdown_period:
            self._check_period_against_breakdown_period(
                args.breakdown_period,
                args.period,
            )

        async with self._storage_engine.get_unit_of_work() as uow:
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            projects = await uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                filter_ref_ids=args.filter_project_ref_ids,
            )
            filter_project_ref_ids = [p.ref_id for p in projects]
            projects_by_ref_id: Dict[EntityId, Project] = {
                p.ref_id: p for p in projects
            }
            projects_by_name: Dict[ProjectName, Project] = {p.name: p for p in projects}

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            habit_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.chore_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            big_plan_collection = (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            metrics = await uow.metric_repository.find_all(
                parent_ref_id=metric_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=args.filter_metric_ref_ids,
            )
            metrics_by_ref_id: Dict[EntityId, Metric] = {m.ref_id: m for m in metrics}

            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            persons = await uow.person_repository.find_all(
                parent_ref_id=person_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=args.filter_person_ref_ids,
            )
            persons_by_ref_id = {p.ref_id: p for p in persons}

            schedule = schedules.get_schedule(
                args.period,
                EntityName("Helper"),
                args.today.to_timestamp_at_end_of_day(),
                user.timezone,
                None,
                None,
                None,
                None,
                None,
                None,
            )

            raw_all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=filter_sources,
                filter_project_ref_ids=filter_project_ref_ids,
                filter_last_modified_time_start=schedule.first_day.start_of_day(),
                filter_last_modified_time_end=schedule.end_day.next_day(),
            )
            all_inbox_tasks = [
                it
                for it in raw_all_inbox_tasks
                # (source is BIG_PLAN and (need to filter then (big_plan_ref_id in filter))
                if it.source is InboxTaskSource.USER
                or (
                    it.source is InboxTaskSource.BIG_PLAN
                    and (
                        not (args.filter_big_plan_ref_ids is not None)
                        or (
                            it.big_plan_ref_id is not None
                            and it.big_plan_ref_id in args.filter_big_plan_ref_ids
                        )
                    )
                )
                or (
                    it.source is InboxTaskSource.HABIT
                    and (
                        not (args.filter_habit_ref_ids is not None)
                        or (
                            it.habit_ref_id is not None
                            and it.habit_ref_id in args.filter_habit_ref_ids
                        )
                    )
                )
                or (
                    it.source is InboxTaskSource.CHORE
                    and (
                        not (args.filter_chore_ref_ids is not None)
                        or (
                            it.chore_ref_id is not None
                            and it.chore_ref_id in args.filter_chore_ref_ids
                        )
                    )
                )
                or (
                    it.source is InboxTaskSource.METRIC
                    and (
                        not (args.filter_metric_ref_ids is not None)
                        or it.metric_ref_id in metrics_by_ref_id
                    )
                )
                or (
                    (
                        it.source is InboxTaskSource.PERSON_CATCH_UP
                        or it.source is InboxTaskSource.PERSON_BIRTHDAY
                    )
                    and (
                        not (args.filter_person_ref_ids is not None)
                        or it.person_ref_id in persons_by_ref_id
                    )
                )
                or (
                    it.source is InboxTaskSource.SLACK_TASK
                    and (
                        not (args.filter_slack_task_ref_ids is not None)
                        or (
                            it.slack_task_ref_id is not None
                            and it.slack_task_ref_id in args.filter_slack_task_ref_ids
                        )
                    )
                )
                or (
                    it.source is InboxTaskSource.EMAIL_TASK
                    and (
                        not (args.filter_email_task_ref_ids is not None)
                        or (
                            it.email_task_ref_id is not None
                            and it.email_task_ref_id in args.filter_email_task_ref_ids
                        )
                    )
                )
            ]

            all_habits = await uow.habit_repository.find_all_with_filters(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=args.filter_habit_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )
            all_habits_by_ref_id: Dict[EntityId, Habit] = {
                rt.ref_id: rt for rt in all_habits
            }

            all_chores = await uow.chore_repository.find_all_with_filters(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=args.filter_chore_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )
            all_chores_by_ref_id: Dict[EntityId, Chore] = {
                rt.ref_id: rt for rt in all_chores
            }

            all_big_plans = await uow.big_plan_repository.find_all_with_filters(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=args.filter_big_plan_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )
            big_plans_by_ref_id: Dict[EntityId, BigPlan] = {
                bp.ref_id: bp for bp in all_big_plans
            }

        global_inbox_tasks_summary = self._run_report_for_inbox_tasks(
            schedule,
            all_inbox_tasks,
        )

        if workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
            global_big_plans_summary = self._run_report_for_big_plan(
                schedule,
                all_big_plans,
            )
        else:
            global_big_plans_summary = WorkableSummary(
                created_cnt=0,
                accepted_cnt=0,
                working_cnt=0,
                not_done_cnt=0,
                done_cnt=0,
                not_done_big_plans=[],
                done_big_plans=[],
            )

        # Build per project breakdown

        if workspace.is_feature_available(WorkspaceFeature.PROJECTS):
            # all_inbox_tasks.groupBy(it -> it.project.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
            per_project_inbox_tasks_summary = {
                k: self._run_report_for_inbox_tasks(schedule, (vx[1] for vx in v))
                for (k, v) in groupby(
                    sorted(
                        [
                            (projects_by_ref_id[it.project_ref_id].name, it)
                            for it in all_inbox_tasks
                        ],
                        key=itemgetter(0),
                    ),
                    key=itemgetter(0),
                )
            }

            if workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
                # all_big_plans.groupBy(it -> it.project..name).map((k, v) -> (k, run_report_for_group(v))).asDict()
                per_project_big_plans_summary = {
                    k: self._run_report_for_big_plan(schedule, (vx[1] for vx in v))
                    for (k, v) in groupby(
                        sorted(
                            [
                                (projects_by_ref_id[bp.project_ref_id].name, bp)
                                for bp in all_big_plans
                            ],
                            key=itemgetter(0),
                        ),
                        key=itemgetter(0),
                    )
                }
            else:
                per_project_big_plans_summary = {}

            per_project_breakdown = [
                PerProjectBreakdownItem(
                    ref_id=projects_by_name[s].ref_id,
                    name=s,
                    inbox_tasks_summary=v,
                    big_plans_summary=per_project_big_plans_summary.get(
                        s,
                        WorkableSummary(0, 0, 0, 0, 0, [], []),
                    ),
                )
                for (s, v) in per_project_inbox_tasks_summary.items()
            ]
        else:
            per_project_breakdown = []

        # Build per period breakdown
        per_period_breakdown = []
        if args.breakdown_period:
            all_schedules = {}
            curr_date = schedule.first_day.start_of_day()
            end_date = schedule.end_day.end_of_day()
            while curr_date < end_date and curr_date <= args.today:
                phase_schedule = schedules.get_schedule(
                    args.breakdown_period,
                    EntityName("Sub-period"),
                    curr_date.to_timestamp_at_end_of_day(),
                    user.timezone,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                )
                all_schedules[phase_schedule.full_name] = phase_schedule
                curr_date = curr_date.next_day()

            per_period_inbox_tasks_summary = {
                k: self._run_report_for_inbox_tasks(v, all_inbox_tasks)
                for (k, v) in all_schedules.items()
            }
            per_period_big_plans_summary = {
                k: self._run_report_for_big_plan(v, all_big_plans)
                for (k, v) in all_schedules.items()
            }
            per_period_breakdown = [
                PerPeriodBreakdownItem(
                    name=k,
                    inbox_tasks_summary=v,
                    big_plans_summary=per_period_big_plans_summary.get(
                        k,
                        WorkableSummary(0, 0, 0, 0, 0, [], []),
                    ),
                )
                for (k, v) in per_period_inbox_tasks_summary.items()
            ]

        # Build per habit breakdown

        # all_inbox_tasks.groupBy(it -> it.habit.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        if workspace.is_feature_available(WorkspaceFeature.HABITS):
            per_habit_breakdown = [
                hb
                for hb in (
                    PerHabitBreakdownItem(
                        ref_id=all_habits_by_ref_id[k].ref_id,
                        name=all_habits_by_ref_id[k].name,
                        archived=all_habits_by_ref_id[k].archived,
                        suspended=all_habits_by_ref_id[k].suspended,
                        period=all_habits_by_ref_id[k].gen_params.period,
                        summary=self._run_report_for_inbox_for_recurring_tasks(
                            schedule,
                            [vx[1] for vx in v],
                        ),
                    )
                    for (k, v) in groupby(
                        sorted(
                            [
                                (it.habit_ref_id, it)
                                for it in all_inbox_tasks
                                if it.habit_ref_id
                            ],
                            key=itemgetter(0),
                        ),
                        key=itemgetter(0),
                    )
                )
                if all_habits_by_ref_id[hb.ref_id].archived is False
            ]
        else:
            per_habit_breakdown = []

        # Build per chore breakdown

        # all_inbox_tasks.groupBy(it -> it.chore.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        if workspace.is_feature_available(WorkspaceFeature.CHORES):
            per_chore_breakdown = [
                cb
                for cb in (
                    PerChoreBreakdownItem(
                        ref_id=all_chores_by_ref_id[k].ref_id,
                        name=all_chores_by_ref_id[k].name,
                        suspended=all_chores_by_ref_id[k].suspended,
                        archived=all_chores_by_ref_id[k].archived,
                        period=all_chores_by_ref_id[k].gen_params.period,
                        summary=self._run_report_for_inbox_for_recurring_tasks(
                            schedule,
                            [vx[1] for vx in v],
                        ),
                    )
                    for (k, v) in groupby(
                        sorted(
                            [
                                (it.chore_ref_id, it)
                                for it in all_inbox_tasks
                                if it.chore_ref_id
                            ],
                            key=itemgetter(0),
                        ),
                        key=itemgetter(0),
                    )
                )
                if all_chores_by_ref_id[cb.ref_id].archived is False
            ]
        else:
            per_chore_breakdown = []

        # Build per big plan breakdown

        # all_inbox_tasks.groupBy(it -> it.bigPlan.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        if workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
            per_big_plan_breakdown = [
                bb
                for bb in (
                    PerBigPlanBreakdownItem(
                        ref_id=big_plans_by_ref_id[k].ref_id,
                        name=big_plans_by_ref_id[k].name,
                        actionable_date=big_plans_by_ref_id[k].actionable_date,
                        summary=self._run_report_for_inbox_tasks_for_big_plan(
                            schedule,
                            (vx[1] for vx in v),
                        ),
                    )
                    for (k, v) in groupby(
                        sorted(
                            [
                                (it.big_plan_ref_id, it)
                                for it in all_inbox_tasks
                                if it.big_plan_ref_id
                            ],
                            key=itemgetter(0),
                        ),
                        key=itemgetter(0),
                    )
                )
                if big_plans_by_ref_id[bb.ref_id].archived is False
            ]
        else:
            per_big_plan_breakdown = []

        # Build user scores overview.
        user_score_overview = None
        if user.is_feature_available(UserFeature.GAMIFICATION):
            async with self._storage_engine.get_unit_of_work() as uow:
                user_score_overview = await ScoreOverviewService().do_it(
                    uow, user, args.today.to_timestamp_at_end_of_day()
                )

        return ReportResult(
            today=args.today,
            period=args.period,
            global_inbox_tasks_summary=global_inbox_tasks_summary,
            global_big_plans_summary=global_big_plans_summary,
            per_project_breakdown=per_project_breakdown,
            per_period_breakdown=per_period_breakdown,
            per_habit_breakdown=per_habit_breakdown,
            per_chore_breakdown=per_chore_breakdown,
            per_big_plan_breakdown=per_big_plan_breakdown,
            user_score_overview=user_score_overview,
        )

    @staticmethod
    def _run_report_for_inbox_tasks(
        schedule: Schedule,
        inbox_tasks: Iterable[InboxTask],
    ) -> "InboxTasksSummary":
        created_cnt_total = 0
        created_per_source_cnt: DefaultDict[InboxTaskSource, int] = defaultdict(int)
        accepted_cnt_total = 0
        accepted_per_source_cnt: DefaultDict[InboxTaskSource, int] = defaultdict(int)
        working_cnt_total = 0
        working_per_source_cnt: DefaultDict[InboxTaskSource, int] = defaultdict(int)
        done_cnt_total = 0
        done_per_source_cnt: DefaultDict[InboxTaskSource, int] = defaultdict(int)
        not_done_cnt_total = 0
        not_done_per_source_cnt: DefaultDict[InboxTaskSource, int] = defaultdict(int)

        for inbox_task in inbox_tasks:
            if schedule.contains_timestamp(inbox_task.created_time):
                created_cnt_total += 1
                created_per_source_cnt[inbox_task.source] += 1

            if inbox_task.status.is_accepted and inbox_task.accepted_time is None:
                raise Exception(f"Invalid state for {inbox_task}")

            if inbox_task.status.is_completed and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.completed_time),
            ):
                if inbox_task.status == InboxTaskStatus.DONE:
                    done_cnt_total += 1
                    done_per_source_cnt[inbox_task.source] += 1
                else:
                    not_done_cnt_total += 1
                    not_done_per_source_cnt[inbox_task.source] += 1
            elif inbox_task.status.is_working and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.working_time),
            ):
                working_cnt_total += 1
                working_per_source_cnt[inbox_task.source] += 1
            elif inbox_task.status.is_accepted and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.accepted_time),
            ):
                accepted_cnt_total += 1
                accepted_per_source_cnt[inbox_task.source] += 1

        return InboxTasksSummary(
            created=NestedResult(
                total_cnt=created_cnt_total,
                per_source_cnt=list(
                    NestedResultPerSource(a, b)
                    for a, b in created_per_source_cnt.items()
                ),
            ),
            accepted=NestedResult(
                total_cnt=accepted_cnt_total,
                per_source_cnt=list(
                    NestedResultPerSource(a, b)
                    for a, b in accepted_per_source_cnt.items()
                ),
            ),
            working=NestedResult(
                total_cnt=working_cnt_total,
                per_source_cnt=list(
                    NestedResultPerSource(a, b)
                    for a, b in working_per_source_cnt.items()
                ),
            ),
            not_done=NestedResult(
                total_cnt=not_done_cnt_total,
                per_source_cnt=list(
                    NestedResultPerSource(a, b)
                    for a, b in not_done_per_source_cnt.items()
                ),
            ),
            done=NestedResult(
                total_cnt=done_cnt_total,
                per_source_cnt=list(
                    NestedResultPerSource(a, b) for a, b in done_per_source_cnt.items()
                ),
            ),
        )

    @staticmethod
    def _run_report_for_inbox_tasks_for_big_plan(
        schedule: Schedule,
        inbox_tasks: Iterable[InboxTask],
    ) -> "BigPlanWorkSummary":
        created_cnt = 0
        accepted_cnt = 0
        working_cnt = 0
        done_cnt = 0
        not_done_cnt = 0

        for inbox_task in inbox_tasks:
            if schedule.contains_timestamp(inbox_task.created_time):
                created_cnt += 1

            if inbox_task.status.is_completed and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.completed_time),
            ):
                if inbox_task.status == InboxTaskStatus.DONE:
                    done_cnt += 1
                else:
                    not_done_cnt += 1
            elif inbox_task.status.is_working and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.working_time),
            ):
                working_cnt += 1
            elif inbox_task.status.is_accepted and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.accepted_time),
            ):
                accepted_cnt += 1

        return BigPlanWorkSummary(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            not_done_ratio=not_done_cnt / float(created_cnt)
            if created_cnt > 0
            else 0.0,
            done_cnt=done_cnt,
            done_ratio=done_cnt / float(created_cnt) if created_cnt > 0 else 0,
        )

    @staticmethod
    def _run_report_for_inbox_for_recurring_tasks(
        schedule: Schedule,
        inbox_tasks: List[InboxTask],
    ) -> "RecurringTaskWorkSummary":
        # The simple summary computations here.
        created_cnt = 0
        accepted_cnt = 0
        working_cnt = 0
        done_cnt = 0
        not_done_cnt = 0

        for inbox_task in inbox_tasks:
            if schedule.contains_timestamp(inbox_task.created_time):
                created_cnt += 1

            if inbox_task.status.is_completed and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.completed_time),
            ):
                if inbox_task.status == InboxTaskStatus.DONE:
                    done_cnt += 1
                else:
                    not_done_cnt += 1
            elif inbox_task.status.is_working and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.working_time),
            ):
                working_cnt += 1
            elif inbox_task.status.is_accepted and schedule.contains_timestamp(
                cast(Timestamp, inbox_task.accepted_time),
            ):
                accepted_cnt += 1

        # The streak computations here.
        sorted_inbox_tasks = sorted(
            (it for it in inbox_tasks if schedule.contains_timestamp(it.created_time)),
            key=lambda it: (it.created_time, it.recurring_repeat_index),
        )
        used_skip_once = False
        streak_plot = []

        for inbox_task_idx, inbox_task in enumerate(sorted_inbox_tasks):
            if inbox_task.status == InboxTaskStatus.DONE:
                if inbox_task.recurring_repeat_index is None:
                    streak_plot.append("X")
                elif inbox_task.recurring_repeat_index == 0:
                    streak_plot.append("1")
                else:
                    streak_plot[-1] = str(int(streak_plot[-1], base=10) + 1)
            else:
                if (
                    inbox_task_idx != 0
                    and inbox_task_idx != len(sorted_inbox_tasks) - 1
                    and sorted_inbox_tasks[inbox_task_idx - 1].status
                    == InboxTaskStatus.DONE
                    and sorted_inbox_tasks[inbox_task_idx + 1].status
                    == InboxTaskStatus.DONE
                    and not used_skip_once
                ):
                    used_skip_once = True
                    if inbox_task.recurring_repeat_index is None:
                        streak_plot.append("x")
                    elif inbox_task.recurring_repeat_index == 0:
                        streak_plot.append("1")
                    else:
                        streak_plot[-1] = str(int(streak_plot[-1], base=10) + 1)
                else:
                    used_skip_once = False
                    if inbox_task.recurring_repeat_index is None:
                        streak_plot.append(
                            "."
                            if inbox_task_idx < (len(sorted_inbox_tasks) - 1)
                            else "?",
                        )
                    elif inbox_task.recurring_repeat_index == 0:
                        streak_plot.append(
                            "0"
                            if inbox_task_idx < (len(sorted_inbox_tasks) - 1)
                            else "?",
                        )

        return RecurringTaskWorkSummary(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            not_done_ratio=not_done_cnt / float(created_cnt)
            if created_cnt > 0
            else 0.0,
            done_cnt=done_cnt,
            done_ratio=done_cnt / float(created_cnt) if created_cnt > 0 else 0.0,
            streak_plot="".join(streak_plot),
        )

    @staticmethod
    def _run_report_for_big_plan(
        schedule: Schedule,
        big_plans: Iterable[BigPlan],
    ) -> "WorkableSummary":
        created_cnt = 0
        accepted_cnt = 0
        working_cnt = 0
        not_done_cnt = 0
        done_cnt = 0
        not_done_projects = []
        done_projects = []

        for big_plan in big_plans:
            if schedule.contains_timestamp(big_plan.created_time):
                created_cnt += 1

            if big_plan.status.is_completed and schedule.contains_timestamp(
                cast(Timestamp, big_plan.completed_time),
            ):
                if big_plan.status == BigPlanStatus.DONE:
                    done_cnt += 1
                    done_projects.append(
                        WorkableBigPlan(
                            ref_id=big_plan.ref_id,
                            name=big_plan.name,
                            actionable_date=big_plan.actionable_date,
                        ),
                    )
                else:
                    not_done_cnt += 1
                    not_done_projects.append(
                        WorkableBigPlan(
                            ref_id=big_plan.ref_id,
                            name=big_plan.name,
                            actionable_date=big_plan.actionable_date,
                        ),
                    )
            elif big_plan.status.is_working and schedule.contains_timestamp(
                cast(Timestamp, big_plan.working_time),
            ):
                working_cnt += 1
            elif big_plan.status.is_accepted and schedule.contains_timestamp(
                cast(Timestamp, big_plan.accepted_time),
            ):
                accepted_cnt += 1

        return WorkableSummary(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            done_cnt=done_cnt,
            not_done_cnt=not_done_cnt,
            not_done_big_plans=not_done_projects,
            done_big_plans=done_projects,
        )

    @staticmethod
    def _check_period_against_breakdown_period(
        breakdown_period: RecurringTaskPeriod,
        period: RecurringTaskPeriod,
    ) -> None:
        breakdown_period_idx = [v.value for v in RecurringTaskPeriod].index(
            breakdown_period.value,
        )
        period_idx = [v.value for v in RecurringTaskPeriod].index(period.value)
        if breakdown_period_idx >= period_idx:
            raise InputValidationError(
                f"Cannot breakdown {period.to_nice()} with {breakdown_period.to_nice()}",
            )
