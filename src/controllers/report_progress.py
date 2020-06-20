"""The controller for computing progress reports."""
from dataclasses import dataclass
from itertools import groupby
from operator import itemgetter
from typing import Optional, Iterable, Final, Dict, List

import pendulum
from nested_dataclasses import nested

from models import schedules
from models.basic import ProjectKey, RecurringTaskPeriod, EntityId, InboxTaskStatus, BigPlanStatus
from models.schedules import Schedule
from repository.big_plans import BigPlan
from repository.inbox_tasks import InboxTask
from repository.projects import Project
from repository.recurring_tasks import RecurringTask
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService


@nested()
@dataclass()
class InboxTasksSummary:
    """A bigger summary for inbox tasks."""

    @nested()
    @dataclass()
    class NestedResult:
        """A result broken down by the various sources of inbox tasks."""
        total_cnt: int
        ad_hoc_cnt: int
        from_big_plan_cnt: int
        from_recurring_task_cnt: int

    created: NestedResult
    accepted: NestedResult
    working: NestedResult
    not_done: NestedResult
    done: NestedResult


@nested()
@dataclass()
class WorkableSummary:
    """The reporting summary."""
    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    done_cnt: int


@nested()
@dataclass()
class PerProjectBreakdownItem:
    """The report for a particular project."""
    name: str
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@nested()
@dataclass()
class PerPeriodBreakdownItem:
    """The report for a particular time period."""
    name: str
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@nested()
@dataclass()
class PerBigPlanBreakdownItem:
    """The report for a particular big plan."""
    name: str
    summary: WorkableSummary


@nested()
@dataclass()
class PerRecurringTaskBreakdownItem:
    """The report for a particular recurring task."""
    name: str
    summary: WorkableSummary


@nested()
@dataclass()
class RunReportResponse:
    """Result of the run report call."""
    global_inbox_tasks_summary: InboxTasksSummary
    global_big_plans_summary: WorkableSummary
    per_project_breakdown: List[PerProjectBreakdownItem]
    per_period_breakdown: Optional[List[PerPeriodBreakdownItem]]
    per_big_plan_breakdown: List[PerBigPlanBreakdownItem]
    per_recurring_task_breakdown: List[PerRecurringTaskBreakdownItem]


class ReportProgressController:
    """The controller for computing progress reports."""

    _projects_service = Final[ProjectsService]
    _inbox_tasks_service = Final[InboxTasksService]
    _big_plans_service = Final[BigPlansService]
    _recurring_tasks_service: Final[RecurringTasksService]

    def __init__(
            self, projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            big_plans_service: BigPlansService, recurring_tasks_service: RecurringTasksService) -> None:
        """Constructor."""
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._big_plans_service = big_plans_service
        self._recurring_tasks_service = recurring_tasks_service

    def run_report(
            self, right_now: pendulum.DateTime, project_keys: Optional[Iterable[ProjectKey]],
            big_plan_ref_ids: Optional[Iterable[EntityId]], recurring_task_ref_ids: Optional[Iterable[EntityId]],
            period: RecurringTaskPeriod, breakdown_period: Optional[RecurringTaskPeriod] = None) -> RunReportResponse:
        """Run a progress report."""
        projects = self._projects_service.load_all_projects(filter_keys=project_keys)
        projects_by_ref_id: Dict[EntityId, Project] = {p.ref_id: p for p in projects}
        schedule = schedules.get_schedule(period, "Helper", right_now, None, None, None, None)

        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_project_ref_ids=[p.ref_id for p in projects],
            filter_big_plan_ref_ids=big_plan_ref_ids, filter_recurring_task_ref_ids=recurring_task_ref_ids)
        all_big_plans = self._big_plans_service.load_all_big_plans(
            filter_archived=False, filter_ref_ids=big_plan_ref_ids, filter_project_ref_ids=[p.ref_id for p in projects])
        big_plans_by_ref_id: Dict[EntityId, BigPlan] = {bp.ref_id: bp for bp in all_big_plans}
        all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            filter_archived=False, filter_ref_ids=recurring_task_ref_ids,
            filter_project_ref_ids=[p.ref_id for p in projects])
        all_recurring_tasks_by_ref_id: Dict[EntityId, RecurringTask] = {rt.ref_id: rt for rt in all_recurring_tasks}

        global_inbox_tasks_summary = self._run_report_for_inbox_tasks(schedule, all_inbox_tasks)
        global_big_plans_summary = self._run_report_for_big_plan(schedule, all_big_plans)

        # Build per project breakdown

        # all_inbox_tasks.groupBy(it -> it.project.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        per_project_inbox_tasks_summary = {
            k: self._run_report_for_inbox_tasks(schedule, (vx[1] for vx in v)) for (k, v) in
            groupby(sorted(
                [(projects_by_ref_id[it.project_ref_id].name, it) for it in all_inbox_tasks],
                key=itemgetter(0)),
                    key=itemgetter(0))}
        # all_big_plans.groupBy(it -> it.project..name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        per_project_big_plans_summary = {
            k: self._run_report_for_big_plan(schedule, (vx[1] for vx in v)) for (k, v) in
            groupby(sorted(
                [(projects_by_ref_id[bp.project_ref_id].name, bp) for bp in all_big_plans],
                key=itemgetter(0)),
                    key=itemgetter(0))}
        per_project_breakdown = [
            PerProjectBreakdownItem(
                name=s,
                inbox_tasks_summary=v,
                big_plans_summary=per_project_big_plans_summary.get(s, WorkableSummary(0, 0, 0, 0, 0)))
            for (s, v) in per_project_inbox_tasks_summary.items()]

        # Build per period breakdown
        per_period_breakdown = None
        if breakdown_period:
            all_schedules = {}
            curr_date = schedule.first_day.start_of("day")
            end_date = schedule.end_day.end_of("day")
            while curr_date < end_date and curr_date < right_now:
                phase_schedule = schedules.get_schedule(breakdown_period, "Helper", curr_date, None, None, None, None)
                all_schedules[phase_schedule.full_name] = phase_schedule
                curr_date = curr_date.add(days=1)

            per_period_inbox_tasks_summary = {
                k: self._run_report_for_inbox_tasks(v, all_inbox_tasks) for (k, v) in all_schedules.items()}
            per_period_big_plans_summary = {
                k: self._run_report_for_big_plan(v, all_big_plans) for (k, v) in all_schedules.items()}
            per_period_breakdown = [
                PerPeriodBreakdownItem(
                    name=k,
                    inbox_tasks_summary=v,
                    big_plans_summary=per_period_big_plans_summary.get(k, WorkableSummary(0, 0, 0, 0, 0)))
                for (k, v) in per_period_inbox_tasks_summary.items()]

        # Build per big plan breakdown

        # all_inbox_tasks.groupBy(it -> it.bigPlan.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        per_big_plan_breakdown = [
            PerBigPlanBreakdownItem(k, self._run_report_for_inbox_tasks_quick(schedule, (vx[1] for vx in v)))
            for (k, v) in
            groupby(sorted(
                [(big_plans_by_ref_id[it.big_plan_ref_id].name, it) for it in all_inbox_tasks if it.big_plan_ref_id],
                key=itemgetter(0)),
                    key=itemgetter(0))]

        # Build per recurring task breakdown

        # all_inbox_tasks.groupBy(it -> it.recurringTask.name).map((k, v) -> (k, run_report_for_group(v))).asDict()
        per_recurring_task_breakdown = [
            PerRecurringTaskBreakdownItem(k, self._run_report_for_inbox_tasks_quick(schedule, (vx[1] for vx in v)))
            for (k, v) in
            groupby(sorted(
                [(all_recurring_tasks_by_ref_id[it.recurring_task_ref_id].name, it)
                 for it in all_inbox_tasks if it.recurring_task_ref_id],
                key=itemgetter(0)),
                    key=itemgetter(0))]

        return RunReportResponse(
            global_inbox_tasks_summary=global_inbox_tasks_summary,
            global_big_plans_summary=global_big_plans_summary,
            per_project_breakdown=per_project_breakdown,
            per_period_breakdown=per_period_breakdown,
            per_big_plan_breakdown=per_big_plan_breakdown,
            per_recurring_task_breakdown=per_recurring_task_breakdown)

    @staticmethod
    def _run_report_for_inbox_tasks(schedule: Schedule, inbox_tasks: Iterable[InboxTask]) -> InboxTasksSummary:
        created_cnt_total = 0
        created_cnt_ad_hoc = 0
        created_cnt_from_big_plan = 0
        created_cnt_from_recurring_task = 0
        accepted_cnt_total = 0
        accepted_cnt_ad_hoc = 0
        accepted_cnt_from_big_plan = 0
        accepted_cnt_from_recurring_task = 0
        working_cnt_total = 0
        working_cnt_ad_hoc = 0
        working_cnt_from_big_plan = 0
        working_cnt_from_recurring_task = 0
        done_cnt_total = 0
        done_cnt_ad_hoc = 0
        done_cnt_from_big_plan = 0
        done_cnt_from_recurring_task = 0
        not_done_cnt_total = 0
        not_done_cnt_ad_hoc = 0
        not_done_cnt_from_big_plan = 0
        not_done_cnt_from_recurring_task = 0

        for inbox_task in inbox_tasks:
            if schedule.contains(inbox_task.created_time):
                created_cnt_total += 1
                if inbox_task.big_plan_ref_id is None and inbox_task.recurring_task_ref_id is None:
                    created_cnt_ad_hoc += 1
                elif inbox_task.big_plan_ref_id is None:
                    created_cnt_from_recurring_task += 1
                else:
                    created_cnt_from_big_plan += 1

            if inbox_task.status.is_completed and schedule.contains(inbox_task.completed_time):
                if inbox_task.status == InboxTaskStatus.DONE:
                    done_cnt_total += 1
                    if inbox_task.big_plan_ref_id is None and inbox_task.recurring_task_ref_id is None:
                        done_cnt_ad_hoc += 1
                    elif inbox_task.big_plan_ref_id is None:
                        done_cnt_from_recurring_task += 1
                    else:
                        done_cnt_from_big_plan += 1
                else:
                    not_done_cnt_total += 1
                    if inbox_task.big_plan_ref_id is None and inbox_task.recurring_task_ref_id is None:
                        not_done_cnt_ad_hoc += 1
                    elif inbox_task.big_plan_ref_id is None:
                        not_done_cnt_from_recurring_task += 1
                    else:
                        not_done_cnt_from_big_plan += 1
            elif inbox_task.status.is_working and schedule.contains(inbox_task.working_time):
                working_cnt_total += 1
                if inbox_task.big_plan_ref_id is None and inbox_task.recurring_task_ref_id is None:
                    working_cnt_ad_hoc += 1
                elif inbox_task.big_plan_ref_id is None:
                    working_cnt_from_recurring_task += 1
                else:
                    working_cnt_from_big_plan += 1
            elif inbox_task.status.is_accepted and schedule.contains(inbox_task.accepted_time):
                accepted_cnt_total += 1
                if inbox_task.big_plan_ref_id is None and inbox_task.recurring_task_ref_id is None:
                    accepted_cnt_ad_hoc += 1
                elif inbox_task.big_plan_ref_id is None:
                    accepted_cnt_from_recurring_task += 1
                else:
                    accepted_cnt_from_big_plan += 1

        return InboxTasksSummary(
            created=InboxTasksSummary.NestedResult(
                total_cnt=created_cnt_total,
                ad_hoc_cnt=created_cnt_ad_hoc,
                from_big_plan_cnt=created_cnt_from_big_plan,
                from_recurring_task_cnt=created_cnt_from_recurring_task),
            accepted=InboxTasksSummary.NestedResult(
                total_cnt=accepted_cnt_total,
                ad_hoc_cnt=accepted_cnt_ad_hoc,
                from_big_plan_cnt=accepted_cnt_from_big_plan,
                from_recurring_task_cnt=accepted_cnt_from_recurring_task),
            working=InboxTasksSummary.NestedResult(
                total_cnt=working_cnt_total,
                ad_hoc_cnt=working_cnt_ad_hoc,
                from_big_plan_cnt=working_cnt_from_big_plan,
                from_recurring_task_cnt=working_cnt_from_recurring_task),
            not_done=InboxTasksSummary.NestedResult(
                total_cnt=not_done_cnt_total,
                ad_hoc_cnt=not_done_cnt_ad_hoc,
                from_big_plan_cnt=not_done_cnt_from_big_plan,
                from_recurring_task_cnt=not_done_cnt_from_recurring_task),
            done=InboxTasksSummary.NestedResult(
                total_cnt=done_cnt_total,
                ad_hoc_cnt=done_cnt_ad_hoc,
                from_big_plan_cnt=done_cnt_from_big_plan,
                from_recurring_task_cnt=done_cnt_from_recurring_task))

    @staticmethod
    def _run_report_for_inbox_tasks_quick(schedule: Schedule, inbox_tasks: Iterable[InboxTask]) -> WorkableSummary:
        created_cnt = 0
        accepted_cnt = 0
        working_cnt = 0
        done_cnt = 0
        not_done_cnt = 0

        for inbox_task in inbox_tasks:
            if schedule.contains(inbox_task.created_time):
                created_cnt += 1

            if inbox_task.status.is_completed and schedule.contains(inbox_task.completed_time):
                if inbox_task.status == InboxTaskStatus.DONE:
                    done_cnt += 1
                else:
                    not_done_cnt += 1
            elif inbox_task.status.is_working and schedule.contains(inbox_task.working_time):
                working_cnt += 1
            elif inbox_task.status.is_accepted and schedule.contains(inbox_task.accepted_time):
                accepted_cnt += 1

        return WorkableSummary(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            done_cnt=done_cnt)

    @staticmethod
    def _run_report_for_big_plan(schedule: Schedule, big_plans: Iterable[BigPlan]) -> WorkableSummary:
        created_cnt = 0
        accepted_cnt = 0
        working_cnt = 0
        not_done_cnt = 0
        done_cnt = 0

        for big_plan in big_plans:
            if schedule.contains(big_plan.created_time):
                created_cnt += 1

            if big_plan.status.is_completed and schedule.contains(big_plan.completed_time):
                if big_plan.status == BigPlanStatus.DONE:
                    done_cnt += 1
                else:
                    not_done_cnt += 1
            elif big_plan.status.is_working and schedule.contains(big_plan.working_time):
                working_cnt += 1
            elif big_plan.status.is_accepted and schedule.contains(big_plan.accepted_time):
                accepted_cnt += 1

        return WorkableSummary(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            done_cnt=done_cnt,
            not_done_cnt=not_done_cnt)
