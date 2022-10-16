"""The command for generating new tasks."""
import typing
from collections import defaultdict
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List, Dict, Tuple, FrozenSet

from jupiter.domain import schedules
from jupiter.domain.chores.chore import Chore
from jupiter.domain.habits.habit import Habit
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.vacation import Vacation
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
    MarkProgressStatus,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider


class GenUseCase(AppMutationUseCase["GenUseCase.Args", None]):
    """The command for generating new tasks."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        right_now: Timestamp
        gen_targets: Iterable[SyncTarget]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_habit_ref_ids: Optional[Iterable[EntityId]]
        filter_chore_ref_ids: Optional[Iterable[EntityId]]
        filter_metric_keys: Optional[Iterable[MetricKey]]
        filter_person_ref_ids: Optional[Iterable[EntityId]]
        filter_slack_task_ref_ids: Optional[Iterable[EntityId]]
        filter_period: Optional[Iterable[RecurringTaskPeriod]]
        sync_even_if_not_modified: bool

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_parent(
                workspace.ref_id
            )
            all_vacations = uow.vacation_repository.find_all(
                parent_ref_id=vacation_collection.ref_id
            )
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            all_projects = uow.project_repository.find_all(
                parent_ref_id=project_collection.ref_id
            )
            all_syncable_projects = uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                filter_keys=args.filter_project_keys,
            )
            all_projects_by_ref_id = {p.ref_id: p for p in all_projects}
            filter_project_ref_ids = [p.ref_id for p in all_syncable_projects]

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            habit_collection = uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )

        if SyncTarget.HABITS in args.gen_targets:
            with progress_reporter.section("Generating habits"):
                with self._storage_engine.get_unit_of_work() as uow:
                    all_habits = uow.habit_repository.find_all_with_filters(
                        parent_ref_id=habit_collection.ref_id,
                        filter_ref_ids=args.filter_habit_ref_ids,
                        filter_project_ref_ids=filter_project_ref_ids,
                    )

                with self._storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.HABIT],
                            allow_archived=True,
                            filter_habit_ref_ids=(rt.ref_id for rt in all_habits),
                        )
                    )

                all_inbox_tasks_by_habit_ref_id_and_timeline: Dict[
                    Tuple[EntityId, str], List[InboxTask]
                ] = defaultdict(list)
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.habit_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'"
                        )
                    all_inbox_tasks_by_habit_ref_id_and_timeline[
                        (inbox_task.habit_ref_id, inbox_task.recurring_timeline)
                    ].append(inbox_task)

                for habit in all_habits:
                    project = all_projects_by_ref_id[habit.project_ref_id]
                    self._generate_inbox_tasks_for_habit(
                        progress_reporter=progress_reporter,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period)
                        if args.filter_period
                        else None,
                        habit=habit,
                        all_inbox_tasks_by_habit_ref_id_and_timeline=all_inbox_tasks_by_habit_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                    )

        if SyncTarget.CHORES in args.gen_targets:
            with progress_reporter.section("Generating chores"):
                with self._storage_engine.get_unit_of_work() as uow:
                    all_chores = uow.chore_repository.find_all_with_filters(
                        parent_ref_id=chore_collection.ref_id,
                        filter_ref_ids=args.filter_chore_ref_ids,
                        filter_project_ref_ids=filter_project_ref_ids,
                    )

                with self._storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.CHORE],
                            allow_archived=True,
                            filter_chore_ref_ids=(rt.ref_id for rt in all_chores),
                        )
                    )

                all_inbox_tasks_by_chore_ref_id_and_timeline = {}
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.chore_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'"
                        )
                    all_inbox_tasks_by_chore_ref_id_and_timeline[
                        (inbox_task.chore_ref_id, inbox_task.recurring_timeline)
                    ] = inbox_task

                for chore in all_chores:
                    project = all_projects_by_ref_id[chore.project_ref_id]
                    self._generate_inbox_tasks_for_chore(
                        progress_reporter=progress_reporter,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period)
                        if args.filter_period
                        else None,
                        all_vacations=all_vacations,
                        chore=chore,
                        all_inbox_tasks_by_chore_ref_id_and_timeline=all_inbox_tasks_by_chore_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                    )

        if SyncTarget.METRICS in args.gen_targets:
            with progress_reporter.section("Generating for metrics"):
                with self._storage_engine.get_unit_of_work() as uow:
                    metric_collection = uow.metric_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                    all_metrics = uow.metric_repository.find_all(
                        parent_ref_id=metric_collection.ref_id,
                        filter_keys=args.filter_metric_keys,
                    )

                    all_collection_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.METRIC],
                            allow_archived=True,
                            filter_metric_ref_ids=[m.ref_id for m in all_metrics],
                        )
                    )

                all_collection_inbox_tasks_by_metric_ref_id_and_timeline = {}

                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.metric_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'"
                        )
                    all_collection_inbox_tasks_by_metric_ref_id_and_timeline[
                        (inbox_task.metric_ref_id, inbox_task.recurring_timeline)
                    ] = inbox_task

                for metric in all_metrics:
                    if metric.collection_params is None:
                        continue

                    # MyPy not smart enough to infer that if (not A and not B) then (A or B)
                    project = all_projects_by_ref_id[
                        metric_collection.collection_project_ref_id
                    ]
                    self._generate_collection_inbox_tasks_for_metric(
                        progress_reporter=progress_reporter,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period)
                        if args.filter_period
                        else None,
                        metric=metric,
                        collection_params=metric.collection_params,
                        all_inbox_tasks_by_metric_ref_id_and_timeline=all_collection_inbox_tasks_by_metric_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                    )

        if SyncTarget.PERSONS in args.gen_targets:
            with progress_reporter.section("Generating for persons"):
                with self._storage_engine.get_unit_of_work() as uow:
                    person_collection = uow.person_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                    all_persons = uow.person_repository.find_all(
                        parent_ref_id=person_collection.ref_id,
                        filter_ref_ids=args.filter_person_ref_ids,
                    )

                    all_catch_up_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                            filter_person_ref_ids=[m.ref_id for m in all_persons],
                        )
                    )
                    all_birthday_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                            filter_person_ref_ids=[m.ref_id for m in all_persons],
                        )
                    )

                all_catch_up_inbox_tasks_by_person_ref_id_and_timeline = {}
                for inbox_task in all_catch_up_inbox_tasks:
                    if (
                        inbox_task.person_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'"
                        )
                    all_catch_up_inbox_tasks_by_person_ref_id_and_timeline[
                        (inbox_task.person_ref_id, inbox_task.recurring_timeline)
                    ] = inbox_task

                project = all_projects_by_ref_id[
                    person_collection.catch_up_project_ref_id
                ]

                for person in all_persons:
                    if person.catch_up_params is None:
                        continue

                    # MyPy not smart enough to infer that if (not A and not B) then (A or B)

                    self._generate_catch_up_inbox_tasks_for_person(
                        progress_reporter=progress_reporter,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period)
                        if args.filter_period
                        else None,
                        person=person,
                        catch_up_params=person.catch_up_params,
                        all_inbox_tasks_by_person_ref_id_and_timeline=all_catch_up_inbox_tasks_by_person_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                    )

            all_birthday_inbox_tasks_by_person_ref_id_and_timeline = {}
            for inbox_task in all_birthday_inbox_tasks:
                if (
                    inbox_task.person_ref_id is None
                    or inbox_task.recurring_timeline is None
                ):
                    raise Exception(
                        f"Expected that inbox task with id='{inbox_task.ref_id}'"
                    )
                all_birthday_inbox_tasks_by_person_ref_id_and_timeline[
                    (inbox_task.person_ref_id, inbox_task.recurring_timeline)
                ] = inbox_task

            for person in all_persons:
                if person.birthday is None:
                    continue

                self._generate_birthday_inbox_task_for_person(
                    progress_reporter=progress_reporter,
                    inbox_task_collection=inbox_task_collection,
                    project=project,
                    right_now=args.right_now,
                    person=person,
                    birthday=person.birthday,
                    all_inbox_tasks_by_person_ref_id_and_timeline=all_birthday_inbox_tasks_by_person_ref_id_and_timeline,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                )

        if SyncTarget.SLACK_TASKS in args.gen_targets:
            with progress_reporter.section("Generating for Slack tasks"):
                with self._storage_engine.get_unit_of_work() as uow:
                    push_integration_group = (
                        uow.push_integration_group_repository.load_by_parent(
                            workspace.ref_id
                        )
                    )
                    slack_collection = (
                        uow.slack_task_collection_repository.load_by_parent(
                            push_integration_group.ref_id
                        )
                    )

                    all_slack_tasks = uow.slack_task_repository.find_all(
                        parent_ref_id=slack_collection.ref_id,
                        filter_ref_ids=args.filter_slack_task_ref_ids,
                    )
                    all_slack_inbox_tasks = (
                        uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.SLACK_TASK],
                            allow_archived=True,
                            filter_slack_task_ref_ids=[
                                st.ref_id for st in all_slack_tasks
                            ],
                        )
                    )

                all_inbox_tasks_by_slack_task_ref_id = {
                    it.slack_task_ref_id: it for it in all_slack_inbox_tasks
                }
                for slack_task in all_slack_tasks:
                    project = all_projects_by_ref_id[
                        slack_collection.generation_project_ref_id
                    ]
                    self._generate_slack_inbox_task_for_slack_task(
                        progress_reporter=progress_reporter,
                        slack_task=slack_task,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        all_inbox_tasks_by_slack_task_ref_id=typing.cast(
                            Dict[EntityId, InboxTask],
                            all_inbox_tasks_by_slack_task_ref_id,
                        ),
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                    )

    def _generate_inbox_tasks_for_habit(
        self,
        progress_reporter: ProgressReporter,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        right_now: Timestamp,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        habit: Habit,
        all_inbox_tasks_by_habit_ref_id_and_timeline: Dict[
            Tuple[EntityId, str], List[InboxTask]
        ],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "habit", habit.ref_id, str(habit.name)
        ) as subprogress_reporter:
            if habit.suspended:
                return

            if (
                period_filter is not None
                and habit.gen_params.period not in period_filter
            ):
                return

            schedule = schedules.get_schedule(
                habit.gen_params.period,
                habit.name,
                right_now,
                self._global_properties.timezone,
                habit.skip_rule,
                habit.gen_params.actionable_from_day,
                habit.gen_params.actionable_from_month,
                habit.gen_params.due_at_time,
                habit.gen_params.due_at_day,
                habit.gen_params.due_at_month,
            )

            if schedule.should_skip:
                return

            all_found_tasks_by_repeat_index: Dict[Optional[int], InboxTask] = {
                ft.recurring_repeat_index: ft
                for ft in all_inbox_tasks_by_habit_ref_id_and_timeline.get(
                    (habit.ref_id, schedule.timeline), []
                )
            }
            repeat_idx_to_keep: typing.Set[Optional[int]] = set()

            for task_idx in range(habit.repeats_in_period_count or 1):
                real_task_idx = (
                    task_idx if habit.repeats_in_period_count is not None else None
                )
                found_task = all_found_tasks_by_repeat_index.get(real_task_idx, None)

                if found_task:
                    repeat_idx_to_keep.add(task_idx)

                    with subprogress_reporter.start_updating_entity(
                        "inbox task", found_task.ref_id, str(found_task.name)
                    ) as entity_reporter:
                        if (
                            not sync_even_if_not_modified
                            and found_task.last_modified_time
                            >= habit.last_modified_time
                        ):
                            entity_reporter.mark_not_needed()
                            return

                        found_task = found_task.update_link_to_habit(
                            project_ref_id=project.ref_id,
                            name=schedule.full_name,
                            timeline=schedule.timeline,
                            repeat_index=real_task_idx,
                            actionable_date=schedule.actionable_date,
                            due_date=schedule.due_time,
                            eisen=habit.gen_params.eisen,
                            difficulty=habit.gen_params.difficulty,
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                        entity_reporter.mark_known_name(str(found_task.name))

                        with self._storage_engine.get_unit_of_work() as uow:
                            uow.inbox_task_repository.save(found_task)
                            entity_reporter.mark_local_change()

                        if found_task.archived:
                            entity_reporter.mark_remote_change(
                                MarkProgressStatus.NOT_NEEDED
                            )
                            return

                        direct_info = NotionInboxTask.DirectInfo(
                            all_projects_map={project.ref_id: project},
                            all_big_plans_map={},
                        )
                        notion_inbox_task = NotionInboxTask.new_notion_entity(
                            found_task, direct_info
                        )
                        self._inbox_task_notion_manager.upsert_leaf(
                            found_task.inbox_task_collection_ref_id,
                            notion_inbox_task,
                        )
                        entity_reporter.mark_remote_change()
                else:
                    inbox_task = InboxTask.new_inbox_task_for_habit(
                        inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                        name=schedule.full_name,
                        project_ref_id=project.ref_id,
                        habit_ref_id=habit.ref_id,
                        recurring_task_timeline=schedule.timeline,
                        recurring_task_repeat_index=real_task_idx,
                        recurring_task_gen_right_now=right_now,
                        eisen=habit.gen_params.eisen,
                        difficulty=habit.gen_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )

                    with subprogress_reporter.start_creating_entity(
                        "inbox task", str(inbox_task.name)
                    ) as entity_reporter:
                        with self._storage_engine.get_unit_of_work() as uow:
                            inbox_task = uow.inbox_task_repository.create(inbox_task)
                            entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                            entity_reporter.mark_local_change()

                        direct_info = NotionInboxTask.DirectInfo(
                            all_projects_map={project.ref_id: project},
                            all_big_plans_map={},
                        )
                        notion_inbox_task = NotionInboxTask.new_notion_entity(
                            inbox_task, direct_info
                        )
                        self._inbox_task_notion_manager.upsert_leaf(
                            inbox_task_collection.ref_id,
                            notion_inbox_task,
                        )
                        entity_reporter.mark_remote_change()

            inbox_task_remove_service = InboxTaskRemoveService(
                self._storage_engine, self._inbox_task_notion_manager
            )
            for task in all_found_tasks_by_repeat_index.values():
                if task.recurring_repeat_index is None:
                    continue
                if task.recurring_repeat_index in repeat_idx_to_keep:
                    continue
                inbox_task_remove_service.do_it(progress_reporter, task)

    def _generate_inbox_tasks_for_chore(
        self,
        progress_reporter: ProgressReporter,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        right_now: Timestamp,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        all_vacations: List[Vacation],
        chore: Chore,
        all_inbox_tasks_by_chore_ref_id_and_timeline: Dict[
            Tuple[EntityId, str], InboxTask
        ],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "chore", chore.ref_id, str(chore.name)
        ) as subprogress_reporter:
            if chore.suspended:
                return

            if (
                period_filter is not None
                and chore.gen_params.period not in period_filter
            ):
                return

            schedule = schedules.get_schedule(
                chore.gen_params.period,
                chore.name,
                right_now,
                self._global_properties.timezone,
                chore.skip_rule,
                chore.gen_params.actionable_from_day,
                chore.gen_params.actionable_from_month,
                chore.gen_params.due_at_time,
                chore.gen_params.due_at_day,
                chore.gen_params.due_at_month,
            )

            if not chore.must_do:
                for vacation in all_vacations:
                    if vacation.is_in_vacation(schedule.first_day, schedule.end_day):
                        return

            if not chore.is_in_active_interval(schedule.first_day, schedule.end_day):
                return

            if schedule.should_skip:
                return

            found_task = all_inbox_tasks_by_chore_ref_id_and_timeline.get(
                (chore.ref_id, schedule.timeline), None
            )

            if found_task:
                with subprogress_reporter.start_updating_entity(
                    "inbox task", found_task.ref_id, str(found_task.name)
                ) as entity_reporter:
                    if (
                        not sync_even_if_not_modified
                        and found_task.last_modified_time >= chore.last_modified_time
                    ):
                        entity_reporter.mark_not_needed()
                        return

                    found_task = found_task.update_link_to_chore(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        timeline=schedule.timeline,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        eisen=chore.gen_params.eisen,
                        difficulty=chore.gen_params.difficulty,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(found_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(found_task)
                        entity_reporter.mark_local_change()

                    if found_task.archived:
                        entity_reporter.mark_remote_change(
                            MarkProgressStatus.NOT_NEEDED
                        )
                        return

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        found_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        found_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
            else:
                inbox_task = InboxTask.new_inbox_task_for_chore(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    project_ref_id=project.ref_id,
                    chore_ref_id=chore.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_gen_right_now=right_now,
                    eisen=chore.gen_params.eisen,
                    difficulty=chore.gen_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                with subprogress_reporter.start_creating_entity(
                    "inbox task", str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task = uow.inbox_task_repository.create(inbox_task)
                        entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        inbox_task_collection.ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _generate_collection_inbox_tasks_for_metric(
        self,
        progress_reporter: ProgressReporter,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        right_now: Timestamp,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        metric: Metric,
        collection_params: RecurringTaskGenParams,
        all_inbox_tasks_by_metric_ref_id_and_timeline: Dict[
            Tuple[EntityId, str], InboxTask
        ],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "metric", metric.ref_id, str(metric.name)
        ) as subprogress_reporter:
            if (
                period_filter is not None
                and collection_params.period not in period_filter
            ):
                return

            schedule = schedules.get_schedule(
                typing.cast(RecurringTaskPeriod, collection_params.period),
                metric.name,
                right_now,
                self._global_properties.timezone,
                None,
                collection_params.actionable_from_day,
                collection_params.actionable_from_month,
                collection_params.due_at_time,
                collection_params.due_at_day,
                collection_params.due_at_month,
            )

            found_task = all_inbox_tasks_by_metric_ref_id_and_timeline.get(
                (metric.ref_id, schedule.timeline), None
            )

            if found_task:
                with subprogress_reporter.start_updating_entity(
                    "inbox task", found_task.ref_id, str(found_task.name)
                ) as entity_reporter:
                    if (
                        not sync_even_if_not_modified
                        and found_task.last_modified_time >= metric.last_modified_time
                    ):
                        entity_reporter.mark_not_needed()
                        return

                    found_task = found_task.update_link_to_metric(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=collection_params.eisen,
                        difficulty=collection_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(found_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(found_task)
                        entity_reporter.mark_local_change()

                    if found_task.archived:
                        entity_reporter.mark_remote_change(
                            MarkProgressStatus.NOT_NEEDED
                        )
                        return

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        found_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        found_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
            else:
                inbox_task = InboxTask.new_inbox_task_for_metric_collection(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    metric_ref_id=metric.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_gen_right_now=right_now,
                    eisen=collection_params.eisen,
                    difficulty=collection_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                with subprogress_reporter.start_creating_entity(
                    "inbox task", str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task = uow.inbox_task_repository.create(inbox_task)
                        entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        inbox_task_collection.ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _generate_catch_up_inbox_tasks_for_person(
        self,
        progress_reporter: ProgressReporter,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        right_now: Timestamp,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        person: Person,
        catch_up_params: RecurringTaskGenParams,
        all_inbox_tasks_by_person_ref_id_and_timeline: Dict[
            Tuple[EntityId, str], InboxTask
        ],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "person", person.ref_id, str(person.name)
        ) as subprogress_reporter:
            if (
                period_filter is not None
                and catch_up_params.period not in period_filter
            ):
                return

            schedule = schedules.get_schedule(
                typing.cast(RecurringTaskPeriod, catch_up_params.period),
                person.name,
                right_now,
                self._global_properties.timezone,
                None,
                catch_up_params.actionable_from_day,
                catch_up_params.actionable_from_month,
                catch_up_params.due_at_time,
                catch_up_params.due_at_day,
                catch_up_params.due_at_month,
            )

            found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
                (person.ref_id, schedule.timeline), None
            )

            if found_task:
                with subprogress_reporter.start_updating_entity(
                    "inbox task", found_task.ref_id, str(found_task.name)
                ) as entity_reporter:
                    if (
                        not sync_even_if_not_modified
                        and found_task.last_modified_time >= person.last_modified_time
                    ):
                        entity_reporter.mark_not_needed()
                        return

                    found_task = found_task.update_link_to_person_catch_up(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=catch_up_params.eisen,
                        difficulty=catch_up_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(found_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(found_task)
                        entity_reporter.mark_local_change()

                    if found_task.archived:
                        entity_reporter.mark_remote_change(
                            MarkProgressStatus.NOT_NEEDED
                        )
                        return

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        found_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        found_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
            else:
                inbox_task = InboxTask.new_inbox_task_for_person_catch_up(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    project_ref_id=project.ref_id,
                    person_ref_id=person.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_gen_right_now=right_now,
                    eisen=catch_up_params.eisen,
                    difficulty=catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                with subprogress_reporter.start_creating_entity(
                    "inbox task", str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task = uow.inbox_task_repository.create(inbox_task)
                        entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        inbox_task_collection.ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _generate_birthday_inbox_task_for_person(
        self,
        progress_reporter: ProgressReporter,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        right_now: Timestamp,
        person: Person,
        birthday: PersonBirthday,
        all_inbox_tasks_by_person_ref_id_and_timeline: Dict[
            Tuple[EntityId, str], InboxTask
        ],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "person", person.ref_id, str(person.name)
        ) as subprogress_reporter:
            schedule = schedules.get_schedule(
                RecurringTaskPeriod.YEARLY,
                person.name,
                right_now,
                self._global_properties.timezone,
                None,
                None,
                None,
                None,
                RecurringTaskDueAtDay.from_raw(
                    RecurringTaskPeriod.MONTHLY, birthday.day
                ),
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY, birthday.month
                ),
            )

            found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
                (person.ref_id, schedule.timeline), None
            )

            if found_task:
                with subprogress_reporter.start_updating_entity(
                    "inbox task", found_task.ref_id, str(found_task.name)
                ) as entity_reporter:
                    if (
                        not sync_even_if_not_modified
                        and found_task.last_modified_time >= person.last_modified_time
                    ):
                        entity_reporter.mark_not_needed()
                        return

                    found_task = found_task.update_link_to_person_birthday(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=schedule.due_time,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(found_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(found_task)
                        entity_reporter.mark_local_change()

                    if found_task.archived:
                        entity_reporter.mark_remote_change(
                            MarkProgressStatus.NOT_NEEDED
                        )
                        return

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        found_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        found_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
            else:
                inbox_task = InboxTask.new_inbox_task_for_person_birthday(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    project_ref_id=project.ref_id,
                    person_ref_id=person.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                    recurring_task_gen_right_now=right_now,
                    due_date=schedule.due_time,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                with subprogress_reporter.start_creating_entity(
                    "inbox task", str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task = uow.inbox_task_repository.create(inbox_task)
                        entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        inbox_task_collection.ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _generate_slack_inbox_task_for_slack_task(
        self,
        progress_reporter: ProgressReporter,
        slack_task: SlackTask,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        all_inbox_tasks_by_slack_task_ref_id: Dict[EntityId, InboxTask],
        sync_even_if_not_modified: bool,
    ) -> None:
        with progress_reporter.start_complex_entity_work(
            "slack task", slack_task.ref_id, str(slack_task.simple_name)
        ) as subprogress_reporter:
            found_task = all_inbox_tasks_by_slack_task_ref_id.get(
                slack_task.ref_id, None
            )

            if found_task:
                with subprogress_reporter.start_updating_entity(
                    "inbox task", found_task.ref_id, str(found_task.name)
                ) as entity_reporter:
                    if (
                        not sync_even_if_not_modified
                        and found_task.last_modified_time
                        >= slack_task.last_modified_time
                    ):
                        entity_reporter.mark_not_needed()
                        return

                    found_task = found_task.update_link_to_slack_task(
                        project_ref_id=project.ref_id,
                        user=slack_task.user,
                        channel=slack_task.channel,
                        generation_extra_info=slack_task.generation_extra_info,
                        message=slack_task.message,
                        source=EventSource.SLACK,  # We consider this update as coming from Slack!
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(found_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(found_task)
                        entity_reporter.mark_local_change()

                    if found_task.archived:
                        entity_reporter.mark_remote_change(
                            MarkProgressStatus.NOT_NEEDED
                        )
                        return

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        found_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        found_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
            else:
                inbox_task = InboxTask.new_inbox_task_for_slack_task(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    project_ref_id=project.ref_id,
                    slack_task_ref_id=slack_task.ref_id,
                    user=slack_task.user,
                    channel=slack_task.channel,
                    generation_extra_info=slack_task.generation_extra_info,
                    message=slack_task.message,
                    source=EventSource.SLACK,  # We consider this generation as coming from Slack
                    created_time=self._time_provider.get_current_time(),
                )

                with subprogress_reporter.start_creating_entity(
                    "inbox task", str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        slack_task = slack_task.mark_as_used_for_generation(
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                        uow.slack_task_repository.save(slack_task)

                        inbox_task = uow.inbox_task_repository.create(inbox_task)
                        entity_reporter.mark_known_entity_id(inbox_task.ref_id)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = NotionInboxTask.new_notion_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.upsert_leaf(
                        inbox_task_collection.ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()
