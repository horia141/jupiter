"""Generate tasks for a workspace."""

import typing
from collections import defaultdict
from typing import Dict, Final, FrozenSet, List, Optional, Tuple

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import FeatureUnavailableError, WorkspaceFeature
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import EmailTaskCollection
from jupiter.core.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import SlackTaskCollection
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.domain.user.user import User
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class GenService:
    """Shared service for performing garbage collection."""

    _domain_storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        domain_storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._domain_storage_engine = domain_storage_engine

    async def do_it(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        workspace: Workspace,
        gen_even_if_not_modified: bool,
        today: ADate,
        gen_targets: list[SyncTarget],
        period: Optional[List[RecurringTaskPeriod]],
        filter_project_ref_ids: Optional[List[EntityId]],
        filter_habit_ref_ids: Optional[List[EntityId]],
        filter_chore_ref_ids: Optional[List[EntityId]],
        filter_metric_ref_ids: Optional[List[EntityId]],
        filter_person_ref_ids: Optional[List[EntityId]],
        filter_slack_task_ref_ids: Optional[List[EntityId]],
        filter_email_task_ref_ids: Optional[List[EntityId]],
    ) -> None:
        """Execute the service's action."""
        big_diff = list(
            set(gen_targets).difference(
                workspace.infer_sync_targets_for_enabled_features(gen_targets)
            )
        )
        if len(big_diff) > 0:
            raise FeatureUnavailableError(
                f"Gen targets {','.join(s.value for s in big_diff)} are not supported in this workspace"
            )

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.HABITS)
            and filter_habit_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.HABITS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.CHORES)
            and filter_chore_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.CHORES)
        if (
            not workspace.is_feature_available(WorkspaceFeature.METRICS)
            and filter_metric_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.METRICS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.PERSONS)
            and filter_person_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PERSONS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.SLACK_TASKS)
            and filter_slack_task_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.SLACK_TASKS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.EMAIL_TASKS)
            and filter_email_task_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.EMAIL_TASKS)

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gen_log = await uow.repository_for(GenLog).load_by_parent(workspace.ref_id)
            gen_log_entry = GenLogEntry.new_log_entry(
                ctx,
                gen_log_ref_id=gen_log.ref_id,
                gen_even_if_not_modified=gen_even_if_not_modified,
                today=today,
                gen_targets=gen_targets,
                period=period,
                filter_project_ref_ids=filter_project_ref_ids,
                filter_habit_ref_ids=filter_habit_ref_ids,
                filter_chore_ref_ids=filter_chore_ref_ids,
                filter_metric_ref_ids=filter_metric_ref_ids,
                filter_person_ref_ids=filter_person_ref_ids,
                filter_slack_task_ref_ids=filter_slack_task_ref_ids,
                filter_email_task_ref_ids=filter_email_task_ref_ids,
            )
            gen_log_entry = await uow.repository_for(GenLogEntry).create(gen_log_entry)

            vacation_collection = (
                await uow.repository_for(VacationCollection).load_by_parent(
                    workspace.ref_id,
                )
            )
            all_vacations = await uow.repository_for(Vacation).find_all(
                parent_ref_id=vacation_collection.ref_id,
            )
            project_collection = await uow.repository_for(ProjectCollection).load_by_parent(
                workspace.ref_id,
            )
            all_projects = await uow.repository_for(Project).find_all(
                parent_ref_id=project_collection.ref_id,
            )
            all_syncable_projects = await uow.repository_for(Project).find_all_generic(
                parent_ref_id=project_collection.ref_id,
                allow_archived=False,
                ref_id=filter_project_ref_ids,
            )
            all_projects_by_ref_id = {p.ref_id: p for p in all_projects}
            filter_project_ref_ids = [p.ref_id for p in all_syncable_projects]

            inbox_task_collection = (
                await uow.repository_for(InboxTaskCollection).load_by_parent(
                    workspace.ref_id,
                )
            )
            habit_collection = await uow.repository_for(HabitCollection).load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.repository_for(ChoreCollection).load_by_parent(
                workspace.ref_id,
            )

        if (
            workspace.is_feature_available(WorkspaceFeature.HABITS)
            and SyncTarget.HABITS in gen_targets
        ):
            async with progress_reporter.section("Generating habits"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_habits = await uow.repository_for(Habit).find_all_generic(
                        parent_ref_id=habit_collection.ref_id,
                        allow_archived=False,
                        ref_id=filter_habit_ref_ids,
                        project_ref_id=filter_project_ref_ids,
                    )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.HABIT],
                            allow_archived=True,
                            habit_ref_id=[rt.ref_id for rt in all_habits],
                        )
                    )

                all_inbox_tasks_by_habit_ref_id_and_timeline: Dict[
                    Tuple[EntityId, str],
                    List[InboxTask],
                ] = defaultdict(list)
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.habit_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_inbox_tasks_by_habit_ref_id_and_timeline[
                        (inbox_task.habit_ref_id, inbox_task.recurring_timeline)
                    ].append(inbox_task)

                for habit in all_habits:
                    project = all_projects_by_ref_id[habit.project_ref_id]
                    gen_log_entry = await self._generate_inbox_tasks_for_habit(
                        ctx,
                        progress_reporter=progress_reporter,
                        user=user,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        today=today,
                        period_filter=frozenset(period) if period else None,
                        habit=habit,
                        all_inbox_tasks_by_habit_ref_id_and_timeline=all_inbox_tasks_by_habit_ref_id_and_timeline,
                        gen_even_if_not_modified=gen_even_if_not_modified,
                        gen_log_entry=gen_log_entry,
                    )

        if (
            workspace.is_feature_available(WorkspaceFeature.CHORES)
            and SyncTarget.CHORES in gen_targets
        ):
            async with progress_reporter.section("Generating chores"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_chores = await uow.repository_for(Chore).find_all_generic(
                        parent_ref_id=chore_collection.ref_id,
                        allow_archived=False,
                        ref_id=filter_chore_ref_ids,
                        project_ref_id=filter_project_ref_ids,
                    )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.CHORE],
                            allow_archived=True,
                            chore_ref_id=[rt.ref_id for rt in all_chores],
                        )
                    )

                all_inbox_tasks_by_chore_ref_id_and_timeline = {}
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.chore_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_inbox_tasks_by_chore_ref_id_and_timeline[
                        (inbox_task.chore_ref_id, inbox_task.recurring_timeline)
                    ] = inbox_task

                for chore in all_chores:
                    project = all_projects_by_ref_id[chore.project_ref_id]
                    gen_log_entry = await self._generate_inbox_tasks_for_chore(
                        ctx,
                        progress_reporter=progress_reporter,
                        user=user,
                        workspace=workspace,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        today=today,
                        period_filter=frozenset(period) if period else None,
                        all_vacations=all_vacations,
                        chore=chore,
                        all_inbox_tasks_by_chore_ref_id_and_timeline=all_inbox_tasks_by_chore_ref_id_and_timeline,
                        gen_even_if_not_modified=gen_even_if_not_modified,
                        gen_log_entry=gen_log_entry,
                    )

        if (
            workspace.is_feature_available(WorkspaceFeature.METRICS)
            and SyncTarget.METRICS in gen_targets
        ):
            async with progress_reporter.section("Generating for metrics"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    metric_collection = (
                        await uow.repository_for(MetricCollection).load_by_parent(
                            workspace.ref_id,
                        )
                    )
                    all_metrics = await uow.repository_for(Metric).find_all(
                        parent_ref_id=metric_collection.ref_id,
                        filter_ref_ids=filter_metric_ref_ids,
                    )

                    all_collection_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            filter_sources=[InboxTaskSource.METRIC],
                            allow_archived=True,
                            metric_ref_id=[m.ref_id for m in all_metrics],
                        )
                    )

                all_collection_inbox_tasks_by_metric_ref_id_and_timeline = {}

                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.metric_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
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
                    gen_log_entry = await self._generate_collection_inbox_tasks_for_metric(
                        ctx,
                        progress_reporter=progress_reporter,
                        user=user,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        today=today,
                        period_filter=frozenset(period) if period else None,
                        metric=metric,
                        collection_params=metric.collection_params,
                        all_inbox_tasks_by_metric_ref_id_and_timeline=all_collection_inbox_tasks_by_metric_ref_id_and_timeline,
                        gen_even_if_not_modified=gen_even_if_not_modified,
                        gen_log_entry=gen_log_entry,
                    )

        if (
            workspace.is_feature_available(WorkspaceFeature.PERSONS)
            and SyncTarget.PERSONS in gen_targets
        ):
            async with progress_reporter.section("Generating for persons"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    person_collection = (
                        await uow.repository_for(PersonCollection).load_by_parent(
                            workspace.ref_id,
                        )
                    )
                    all_persons = await uow.repository_for(Person).find_all(
                        parent_ref_id=person_collection.ref_id,
                        filter_ref_ids=filter_person_ref_ids,
                    )

                    all_catch_up_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            source=[InboxTaskSource.PERSON_CATCH_UP],
                            perfon_ref_id=[m.ref_id for m in all_persons],
                        )
                    )
                    all_birthday_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            source=[InboxTaskSource.PERSON_BIRTHDAY],
                            person_ref_id=[m.ref_id for m in all_persons],
                        )
                    )

                all_catch_up_inbox_tasks_by_person_ref_id_and_timeline = {}
                for inbox_task in all_catch_up_inbox_tasks:
                    if (
                        inbox_task.person_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
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

                    gen_log_entry = await self._generate_catch_up_inbox_tasks_for_person(
                        ctx,
                        progress_reporter=progress_reporter,
                        user=user,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        today=today,
                        period_filter=frozenset(period) if period else None,
                        person=person,
                        catch_up_params=person.catch_up_params,
                        all_inbox_tasks_by_person_ref_id_and_timeline=all_catch_up_inbox_tasks_by_person_ref_id_and_timeline,
                        gen_even_if_not_modified=gen_even_if_not_modified,
                        gen_log_entry=gen_log_entry,
                    )

            all_birthday_inbox_tasks_by_person_ref_id_and_timeline = {}
            for inbox_task in all_birthday_inbox_tasks:
                if (
                    inbox_task.person_ref_id is None
                    or inbox_task.recurring_timeline is None
                ):
                    raise Exception(
                        f"Expected that inbox task with id='{inbox_task.ref_id}'",
                    )
                all_birthday_inbox_tasks_by_person_ref_id_and_timeline[
                    (inbox_task.person_ref_id, inbox_task.recurring_timeline)
                ] = inbox_task

            for person in all_persons:
                if person.birthday is None:
                    continue

                gen_log_entry = await self._generate_birthday_inbox_task_for_person(
                    ctx,
                    progress_reporter=progress_reporter,
                    user=user,
                    inbox_task_collection=inbox_task_collection,
                    project=project,
                    today=today,
                    person=person,
                    birthday=person.birthday,
                    all_inbox_tasks_by_person_ref_id_and_timeline=all_birthday_inbox_tasks_by_person_ref_id_and_timeline,
                    gen_even_if_not_modified=gen_even_if_not_modified,
                    gen_log_entry=gen_log_entry,
                )

        if (
            workspace.is_feature_available(WorkspaceFeature.SLACK_TASKS)
            and SyncTarget.SLACK_TASKS in gen_targets
        ):
            async with progress_reporter.section("Generating for Slack tasks"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    push_integration_group = (
                        await uow.repository_for(PushIntegrationGroup).load_by_parent(
                            workspace.ref_id,
                        )
                    )
                    slack_collection = (
                        await uow.repository_for(SlackTaskCollection).load_by_parent(
                            push_integration_group.ref_id,
                        )
                    )

                    all_slack_tasks = await uow.repository_for(SlackTask).find_all(
                        parent_ref_id=slack_collection.ref_id,
                        filter_ref_ids=filter_slack_task_ref_ids,
                    )
                    all_slack_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            source=[InboxTaskSource.SLACK_TASK],
                            slack_task_ref_id=[
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
                    gen_log_entry = (
                        await self._generate_slack_inbox_task_for_slack_task(
                            ctx,
                            progress_reporter=progress_reporter,
                            slack_task=slack_task,
                            inbox_task_collection=inbox_task_collection,
                            project=project,
                            all_inbox_tasks_by_slack_task_ref_id=typing.cast(
                                Dict[EntityId, InboxTask],
                                all_inbox_tasks_by_slack_task_ref_id,
                            ),
                            gen_even_if_not_modified=gen_even_if_not_modified,
                            gen_log_entry=gen_log_entry,
                        )
                    )

        if (
            workspace.is_feature_available(WorkspaceFeature.EMAIL_TASKS)
            and SyncTarget.EMAIL_TASKS in gen_targets
        ):
            async with progress_reporter.section("Generating for email tasks"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    push_integration_group = (
                        await uow.repository_for(PushIntegrationGroup).load_by_parent(
                            workspace.ref_id,
                        )
                    )
                    email_collection = (
                        await uow.repository_for(EmailTaskCollection).load_by_parent(
                            push_integration_group.ref_id,
                        )
                    )

                    all_email_tasks = await uow.repository_for(EmailTask).find_all(
                        parent_ref_id=email_collection.ref_id,
                        filter_ref_ids=filter_email_task_ref_ids,
                    )
                    all_email_inbox_tasks = (
                        await uow.repository_for(InboxTask).find_all_generic(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            source=[InboxTaskSource.EMAIL_TASK],
                            email_task_ref_id=[
                                st.ref_id for st in all_email_tasks
                            ],
                        )
                    )

                all_inbox_tasks_by_email_task_ref_id = {
                    it.email_task_ref_id: it for it in all_email_inbox_tasks
                }
                for email_task in all_email_tasks:
                    project = all_projects_by_ref_id[
                        email_collection.generation_project_ref_id
                    ]
                    gen_log_entry = (
                        await self._generate_email_inbox_task_for_email_task(
                            ctx,
                            progress_reporter=progress_reporter,
                            email_task=email_task,
                            inbox_task_collection=inbox_task_collection,
                            project=project,
                            all_inbox_tasks_by_email_task_ref_id=typing.cast(
                                Dict[EntityId, InboxTask],
                                all_inbox_tasks_by_email_task_ref_id,
                            ),
                            gen_even_if_not_modified=gen_even_if_not_modified,
                            gen_log_entry=gen_log_entry,
                        )
                    )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gen_log_entry = gen_log_entry.close(ctx)
            gen_log_entry = await uow.repository_for(GenLogEntry).save(gen_log_entry)

    async def _generate_inbox_tasks_for_habit(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        habit: Habit,
        all_inbox_tasks_by_habit_ref_id_and_timeline: Dict[
            Tuple[EntityId, str],
            List[InboxTask],
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        if habit.suspended:
            return gen_log_entry

        if period_filter is not None and habit.gen_params.period not in period_filter:
            return gen_log_entry

        schedule = schedules.get_schedule(
            habit.gen_params.period,
            habit.name,
            today.to_timestamp_at_end_of_day(),
            habit.skip_rule,
            habit.gen_params.actionable_from_day,
            habit.gen_params.actionable_from_month,
            habit.gen_params.due_at_day,
            habit.gen_params.due_at_month,
        )

        if schedule.should_skip:
            return gen_log_entry

        all_found_tasks_by_repeat_index: Dict[Optional[int], InboxTask] = {
            ft.recurring_repeat_index: ft
            for ft in all_inbox_tasks_by_habit_ref_id_and_timeline.get(
                (habit.ref_id, schedule.timeline),
                [],
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

                if (
                    not gen_even_if_not_modified
                    and found_task.last_modified_time >= habit.last_modified_time
                ):
                    return gen_log_entry

                found_task = found_task.update_link_to_habit(
                    ctx,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    repeat_index=real_task_idx,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_date,
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    await uow.repository_for(InboxTask).save(found_task)
                    await progress_reporter.mark_updated(found_task)
                gen_log_entry = gen_log_entry.add_entity_updated(
                    ctx,
                    found_task,
                )
            else:
                inbox_task = InboxTask.new_inbox_task_for_habit(
                    ctx,
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    project_ref_id=project.ref_id,
                    habit_ref_id=habit.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_repeat_index=real_task_idx,
                    recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_date,
                )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    inbox_task = await uow.repository_for(InboxTask).create(
                        inbox_task,
                    )
                    await progress_reporter.mark_created(inbox_task)
                gen_log_entry = gen_log_entry.add_entity_created(
                    ctx,
                    inbox_task,
                )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            inbox_task_remove_service = InboxTaskRemoveService()
            for task in all_found_tasks_by_repeat_index.values():
                if task.recurring_repeat_index is None:
                    continue
                if task.recurring_repeat_index in repeat_idx_to_keep:
                    continue
                await inbox_task_remove_service.do_it(ctx, uow, progress_reporter, task)
                gen_log_entry = gen_log_entry.add_entity_removed(
                    ctx,
                    task,
                )

        return gen_log_entry

    async def _generate_inbox_tasks_for_chore(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        workspace: Workspace,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        all_vacations: List[Vacation],
        chore: Chore,
        all_inbox_tasks_by_chore_ref_id_and_timeline: Dict[
            Tuple[EntityId, str],
            InboxTask,
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        if chore.suspended:
            return gen_log_entry

        if period_filter is not None and chore.gen_params.period not in period_filter:
            return gen_log_entry

        schedule = schedules.get_schedule(
            chore.gen_params.period,
            chore.name,
            today.to_timestamp_at_end_of_day(),
            chore.skip_rule,
            chore.gen_params.actionable_from_day,
            chore.gen_params.actionable_from_month,
            chore.gen_params.due_at_day,
            chore.gen_params.due_at_month,
        )

        if workspace.is_feature_available(WorkspaceFeature.VACATIONS):
            if not chore.must_do:
                for vacation in all_vacations:
                    if vacation.is_in_vacation(schedule.first_day, schedule.end_day):
                        return gen_log_entry

        if not chore.is_in_active_interval(schedule.first_day, schedule.end_day):
            return gen_log_entry

        if schedule.should_skip:
            return gen_log_entry

        found_task = all_inbox_tasks_by_chore_ref_id_and_timeline.get(
            (chore.ref_id, schedule.timeline),
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= chore.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_chore(
                ctx,
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                timeline=schedule.timeline,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
                eisen=chore.gen_params.eisen,
                difficulty=chore.gen_params.difficulty,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_chore(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                name=schedule.full_name,
                project_ref_id=project.ref_id,
                chore_ref_id=chore.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
                eisen=chore.gen_params.eisen,
                difficulty=chore.gen_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_collection_inbox_tasks_for_metric(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        metric: Metric,
        collection_params: RecurringTaskGenParams,
        all_inbox_tasks_by_metric_ref_id_and_timeline: Dict[
            Tuple[EntityId, str],
            InboxTask,
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        if period_filter is not None and collection_params.period not in period_filter:
            return gen_log_entry

        schedule = schedules.get_schedule(
            typing.cast(RecurringTaskPeriod, collection_params.period),
            metric.name,
            today.to_timestamp_at_end_of_day(),
            None,
            collection_params.actionable_from_day,
            collection_params.actionable_from_month,
            collection_params.due_at_day,
            collection_params.due_at_month,
        )

        found_task = all_inbox_tasks_by_metric_ref_id_and_timeline.get(
            (metric.ref_id, schedule.timeline),
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= metric.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_metric(
                ctx,
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                recurring_timeline=schedule.timeline,
                eisen=collection_params.eisen,
                difficulty=collection_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_time=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_metric_collection(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                metric_ref_id=metric.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
                eisen=collection_params.eisen,
                difficulty=collection_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_catch_up_inbox_tasks_for_person(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
        person: Person,
        catch_up_params: RecurringTaskGenParams,
        all_inbox_tasks_by_person_ref_id_and_timeline: Dict[
            Tuple[EntityId, str],
            InboxTask,
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        if period_filter is not None and catch_up_params.period not in period_filter:
            return gen_log_entry

        schedule = schedules.get_schedule(
            typing.cast(RecurringTaskPeriod, catch_up_params.period),
            person.name,
            today.to_timestamp_at_end_of_day(),
            None,
            catch_up_params.actionable_from_day,
            catch_up_params.actionable_from_month,
            catch_up_params.due_at_day,
            catch_up_params.due_at_month,
        )

        found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
            (person.ref_id, schedule.timeline),
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= person.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_person_catch_up(
                ctx,
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                recurring_timeline=schedule.timeline,
                eisen=catch_up_params.eisen,
                difficulty=catch_up_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_time=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_person_catch_up(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                name=schedule.full_name,
                project_ref_id=project.ref_id,
                person_ref_id=person.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
                eisen=catch_up_params.eisen,
                difficulty=catch_up_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_birthday_inbox_task_for_person(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        person: Person,
        birthday: PersonBirthday,
        all_inbox_tasks_by_person_ref_id_and_timeline: Dict[
            Tuple[EntityId, str],
            InboxTask,
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        schedule = schedules.get_schedule(
            RecurringTaskPeriod.YEARLY,
            person.name,
            today.to_timestamp_at_end_of_day(),
            None,
            None,
            None,
            RecurringTaskDueAtDay(
                RecurringTaskPeriod.YEARLY,
                birthday.day,
            ),
            RecurringTaskDueAtMonth(
                RecurringTaskPeriod.YEARLY,
                birthday.month,
            ),
        )

        found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
            (person.ref_id, schedule.timeline),
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= person.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_person_birthday(
                ctx,
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                recurring_timeline=schedule.timeline,
                preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                due_time=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_person_birthday(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                name=schedule.full_name,
                project_ref_id=project.ref_id,
                person_ref_id=person.ref_id,
                recurring_task_timeline=schedule.timeline,
                preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
                due_date=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_slack_inbox_task_for_slack_task(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        slack_task: SlackTask,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        all_inbox_tasks_by_slack_task_ref_id: Dict[EntityId, InboxTask],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        found_task = all_inbox_tasks_by_slack_task_ref_id.get(
            slack_task.ref_id,
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= slack_task.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_slack_task(
                ctx,
                project_ref_id=project.ref_id,
                user=slack_task.user,
                channel=slack_task.channel,
                message=slack_task.message,
                generation_extra_info=slack_task.generation_extra_info,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_slack_task(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                project_ref_id=project.ref_id,
                slack_task_ref_id=slack_task.ref_id,
                user=slack_task.user,
                channel=slack_task.channel,
                generation_extra_info=slack_task.generation_extra_info,
                message=slack_task.message,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                slack_task = slack_task.mark_as_used_for_generation(ctx)
                await uow.repository_for(SlackTask).save(slack_task)
                await progress_reporter.mark_updated(slack_task)

                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_email_inbox_task_for_email_task(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        email_task: EmailTask,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        all_inbox_tasks_by_email_task_ref_id: Dict[EntityId, InboxTask],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        found_task = all_inbox_tasks_by_email_task_ref_id.get(
            email_task.ref_id,
            None,
        )

        if found_task:
            if (
                not gen_even_if_not_modified
                and found_task.last_modified_time >= email_task.last_modified_time
            ):
                return gen_log_entry

            found_task = found_task.update_link_to_email_task(
                ctx,
                project_ref_id=project.ref_id,
                from_address=email_task.from_address,
                from_name=email_task.from_name,
                to_address=email_task.to_address,
                subject=email_task.subject,
                body=email_task.body,
                generation_extra_info=email_task.generation_extra_info,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.repository_for(InboxTask).save(found_task)
                await progress_reporter.mark_updated(found_task)

            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_email_task(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                project_ref_id=project.ref_id,
                email_task_ref_id=email_task.ref_id,
                from_address=email_task.from_address,
                from_name=email_task.from_name,
                to_address=email_task.to_address,
                subject=email_task.subject,
                body=email_task.body,
                generation_extra_info=email_task.generation_extra_info,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                email_task = email_task.mark_as_used_for_generation(ctx)
                await uow.repository_for(EmailTask).save(email_task)
                await progress_reporter.mark_updated(email_task)

                inbox_task = await uow.repository_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry
