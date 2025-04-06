"""Generate tasks for a workspace."""

import typing
from collections import defaultdict
from typing import Final, Sequence

from jupiter.core.domain.application.gen.gen_log import GenLog
from jupiter.core.domain.application.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_collection import ChoreCollection
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_collection import HabitCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.persons.person_birthday import PersonBirthday
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.concept.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.concept.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.vacations.vacation import Vacation
from jupiter.core.domain.concept.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.concept.working_mem.working_mem import WorkingMem
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import FeatureUnavailableError, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import NoFilter
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
        period: list[RecurringTaskPeriod] | None,
        filter_project_ref_ids: list[EntityId] | None = None,
        filter_habit_ref_ids: list[EntityId] | None = None,
        filter_chore_ref_ids: list[EntityId] | None = None,
        filter_metric_ref_ids: list[EntityId] | None = None,
        filter_person_ref_ids: list[EntityId] | None = None,
        filter_slack_task_ref_ids: list[EntityId] | None = None,
        filter_email_task_ref_ids: list[EntityId] | None = None,
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
            gen_log = await uow.get_for(GenLog).load_by_parent(workspace.ref_id)
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
            gen_log_entry = await uow.get_for(GenLogEntry).create(gen_log_entry)

            vacation_collection = await uow.get_for(VacationCollection).load_by_parent(
                workspace.ref_id,
            )
            all_vacations = await uow.get_for(Vacation).find_all(
                parent_ref_id=vacation_collection.ref_id,
            )
            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id,
            )
            all_projects = await uow.get_for(Project).find_all(
                parent_ref_id=project_collection.ref_id,
            )
            all_syncable_projects = await uow.get_for(Project).find_all_generic(
                parent_ref_id=project_collection.ref_id,
                allow_archived=False,
                ref_id=filter_project_ref_ids or NoFilter(),
            )
            all_projects_by_ref_id = {p.ref_id: p for p in all_projects}
            filter_project_ref_ids = [p.ref_id for p in all_syncable_projects]

            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            working_mem_collection = await uow.get_for(
                WorkingMemCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            habit_collection = await uow.get_for(HabitCollection).load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
                workspace.ref_id,
            )
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id,
            )
            time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
                workspace.ref_id,
            )

        if (
            workspace.is_feature_available(WorkspaceFeature.WORKING_MEM)
            and SyncTarget.WORKING_MEM in gen_targets
        ):
            async with progress_reporter.section("Generating working mem"):
                all_working_mem_by_timeline = {}
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_working_mem = await uow.get_for(WorkingMem).find_all_generic(
                        parent_ref_id=working_mem_collection.ref_id,
                        allow_archived=False,
                    )
                    for working_mem in all_working_mem:
                        all_working_mem_by_timeline[working_mem.timeline] = working_mem

                all_notes_by_working_mem_ref_id = {}
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_notes = await uow.get_for(Note).find_all_generic(
                        parent_ref_id=note_collection.ref_id,
                        allow_archived=False,
                        domain=NoteDomain.WORKING_MEM,
                        source_entity_ref_id=(
                            [wm.ref_id for wm in all_working_mem]
                            if all_working_mem
                            else NoFilter()
                        ),
                    )
                    for note in all_notes:
                        all_notes_by_working_mem_ref_id[note.source_entity_ref_id] = (
                            note
                        )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_cleanup_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        source=[InboxTaskSource.WORKING_MEM_CLEANUP],
                        allow_archived=True,
                        source_entity_ref_id=(
                            [rt.ref_id for rt in all_working_mem]
                            if all_working_mem
                            else NoFilter()
                        ),
                    )

                all_inbox_tasks_by_working_mem_ref_id_and_timeline = {}
                for inbox_task in all_cleanup_inbox_tasks:
                    if (
                        inbox_task.source_entity_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_inbox_tasks_by_working_mem_ref_id_and_timeline[
                        (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
                    ] = inbox_task

                gen_log_entry = await self._generate_working_mem_and_inbox_task(
                    ctx,
                    progress_reporter=progress_reporter,
                    user=user,
                    workspace=workspace,
                    working_mem_collection=working_mem_collection,
                    note_collection=note_collection,
                    inbox_task_collection=inbox_task_collection,
                    all_working_mem_by_timeline=all_working_mem_by_timeline,
                    all_notes_by_working_mem_ref_id=all_notes_by_working_mem_ref_id,
                    all_inbox_tasks_by_working_mem_ref_id_and_timeline=all_inbox_tasks_by_working_mem_ref_id_and_timeline,
                    today=today,
                    gen_even_if_not_modified=gen_even_if_not_modified,
                    gen_log_entry=gen_log_entry,
                )

        if (
            workspace.is_feature_available(WorkspaceFeature.HABITS)
            and SyncTarget.HABITS in gen_targets
        ):
            async with progress_reporter.section("Generating habits"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_habits = await uow.get_for(Habit).find_all_generic(
                        parent_ref_id=habit_collection.ref_id,
                        allow_archived=False,
                        ref_id=filter_habit_ref_ids or NoFilter(),
                        project_ref_id=filter_project_ref_ids or NoFilter(),
                    )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        source=[InboxTaskSource.HABIT],
                        allow_archived=True,
                        source_entity_ref_id=(
                            [rt.ref_id for rt in all_habits]
                            if all_habits
                            else NoFilter()
                        ),
                    )

                all_inbox_tasks_by_habit_ref_id_and_timeline: dict[
                    tuple[EntityId, str],
                    list[InboxTask],
                ] = defaultdict(list)
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.source_entity_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_inbox_tasks_by_habit_ref_id_and_timeline[
                        (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
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
                    all_chores = await uow.get_for(Chore).find_all_generic(
                        parent_ref_id=chore_collection.ref_id,
                        allow_archived=False,
                        ref_id=filter_chore_ref_ids or NoFilter(),
                        project_ref_id=filter_project_ref_ids or NoFilter(),
                    )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        source=[InboxTaskSource.CHORE],
                        allow_archived=True,
                        source_entity_ref_id=(
                            [rt.ref_id for rt in all_chores]
                            if all_chores
                            else NoFilter()
                        ),
                    )

                all_inbox_tasks_by_chore_ref_id_and_timeline = {}
                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.source_entity_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_inbox_tasks_by_chore_ref_id_and_timeline[
                        (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
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
                    metric_collection = await uow.get_for(
                        MetricCollection
                    ).load_by_parent(
                        workspace.ref_id,
                    )
                    all_metrics = await uow.get_for(Metric).find_all(
                        parent_ref_id=metric_collection.ref_id,
                        filter_ref_ids=filter_metric_ref_ids,
                    )

                    all_collection_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        source=[InboxTaskSource.METRIC],
                        allow_archived=True,
                        source_entity_ref_id=(
                            [m.ref_id for m in all_metrics]
                            if all_metrics
                            else NoFilter()
                        ),
                    )

                all_collection_inbox_tasks_by_metric_ref_id_and_timeline = {}

                for inbox_task in all_collection_inbox_tasks:
                    if (
                        inbox_task.source_entity_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_collection_inbox_tasks_by_metric_ref_id_and_timeline[
                        (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
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
                    person_collection = await uow.get_for(
                        PersonCollection
                    ).load_by_parent(
                        workspace.ref_id,
                    )
                    all_persons = await uow.get_for(Person).find_all(
                        parent_ref_id=person_collection.ref_id,
                        filter_ref_ids=filter_person_ref_ids,
                    )

                    all_catch_up_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        source=[InboxTaskSource.PERSON_CATCH_UP],
                        source_entity_ref_id=(
                            [m.ref_id for m in all_persons]
                            if all_persons
                            else NoFilter()
                        ),
                    )
                    all_birthday_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        source=[InboxTaskSource.PERSON_BIRTHDAY],
                        source_entity_ref_id=(
                            [m.ref_id for m in all_persons]
                            if all_persons
                            else NoFilter()
                        ),
                    )
                    all_birthday_time_event_blocks = await uow.get_for(
                        TimeEventFullDaysBlock
                    ).find_all_generic(
                        parent_ref_id=time_event_domain.ref_id,
                        allow_archived=False,
                        namespace=TimeEventNamespace.PERSON_BIRTHDAY,
                        source_entity_ref_id=(
                            [m.ref_id for m in all_persons]
                            if all_persons
                            else NoFilter()
                        ),
                    )

                all_catch_up_inbox_tasks_by_person_ref_id_and_timeline = {}
                for inbox_task in all_catch_up_inbox_tasks:
                    if (
                        inbox_task.source_entity_ref_id is None
                        or inbox_task.recurring_timeline is None
                    ):
                        raise Exception(
                            f"Expected that inbox task with id='{inbox_task.ref_id}'",
                        )
                    all_catch_up_inbox_tasks_by_person_ref_id_and_timeline[
                        (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
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
                    inbox_task.source_entity_ref_id is None
                    or inbox_task.recurring_timeline is None
                ):
                    raise Exception(
                        f"Expected that inbox task with id='{inbox_task.ref_id}'",
                    )
                all_birthday_inbox_tasks_by_person_ref_id_and_timeline[
                    (inbox_task.source_entity_ref_id, inbox_task.recurring_timeline)
                ] = inbox_task

            all_birthday_time_event_blocks_by_person_ref_id_and_start_date = {}
            for time_event_block in all_birthday_time_event_blocks:
                all_birthday_time_event_blocks_by_person_ref_id_and_start_date[
                    (time_event_block.source_entity_ref_id, time_event_block.start_date)
                ] = time_event_block

            for person in all_persons:
                if person.birthday is None:
                    continue

                for idx in range(5):
                    gen_log_entry = await self._generate_birthday_time_event_block_for_person(
                        ctx,
                        progress_reporter=progress_reporter,
                        time_event_domain=time_event_domain,
                        today=today.add_days(idx * 365),
                        person=person,
                        all_birthday_time_event_blocks_by_person_ref_id_and_start_date=all_birthday_time_event_blocks_by_person_ref_id_and_start_date,
                        gen_even_if_not_modified=gen_even_if_not_modified,
                        gen_log_entry=gen_log_entry,
                    )

                    gen_log_entry = await self._generate_birthday_inbox_task_for_person(
                        ctx,
                        progress_reporter=progress_reporter,
                        user=user,
                        inbox_task_collection=inbox_task_collection,
                        project=project,
                        today=today.add_days(idx * 365),
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
                    push_integration_group = await uow.get_for(
                        PushIntegrationGroup
                    ).load_by_parent(
                        workspace.ref_id,
                    )
                    slack_collection = await uow.get_for(
                        SlackTaskCollection
                    ).load_by_parent(
                        push_integration_group.ref_id,
                    )

                    all_slack_tasks = await uow.get_for(SlackTask).find_all(
                        parent_ref_id=slack_collection.ref_id,
                        filter_ref_ids=filter_slack_task_ref_ids,
                    )
                    all_slack_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        source=[InboxTaskSource.SLACK_TASK],
                        source_entity_ref_id=(
                            [st.ref_id for st in all_slack_tasks]
                            if all_slack_tasks
                            else NoFilter()
                        ),
                    )

                all_inbox_tasks_by_slack_task_ref_id = {
                    it.source_entity_ref_id_for_sure: it for it in all_slack_inbox_tasks
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
                                dict[EntityId, InboxTask],
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
                    push_integration_group = await uow.get_for(
                        PushIntegrationGroup
                    ).load_by_parent(
                        workspace.ref_id,
                    )
                    email_collection = await uow.get_for(
                        EmailTaskCollection
                    ).load_by_parent(
                        push_integration_group.ref_id,
                    )

                    all_email_tasks = await uow.get_for(EmailTask).find_all(
                        parent_ref_id=email_collection.ref_id,
                        filter_ref_ids=filter_email_task_ref_ids,
                    )
                    all_email_inbox_tasks = await uow.get_for(
                        InboxTask
                    ).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        source=[InboxTaskSource.EMAIL_TASK],
                        source_entity_ref_id=(
                            [st.ref_id for st in all_email_tasks]
                            if all_email_tasks
                            else NoFilter()
                        ),
                    )

                all_inbox_tasks_by_email_task_ref_id = {
                    it.source_entity_ref_id_for_sure: it for it in all_email_inbox_tasks
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
                                dict[EntityId, InboxTask],
                                all_inbox_tasks_by_email_task_ref_id,
                            ),
                            gen_even_if_not_modified=gen_even_if_not_modified,
                            gen_log_entry=gen_log_entry,
                        )
                    )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gen_log_entry = gen_log_entry.close(ctx)
            gen_log_entry = await uow.get_for(GenLogEntry).save(gen_log_entry)

    async def _generate_working_mem_and_inbox_task(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        workspace: Workspace,
        working_mem_collection: WorkingMemCollection,
        note_collection: NoteCollection,
        inbox_task_collection: InboxTaskCollection,
        all_working_mem_by_timeline: dict[str, WorkingMem],
        all_notes_by_working_mem_ref_id: dict[EntityId, Note],
        all_inbox_tasks_by_working_mem_ref_id_and_timeline: dict[
            tuple[EntityId, str],
            InboxTask,
        ],
        today: ADate,
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        schedule = schedules.get_schedule(
            working_mem_collection.generation_period,
            EntityName("Cleanup WorkingMem.txt"),
            today.to_timestamp_at_end_of_day(),
            None,
            None,
            None,
            None,
            None,
        )

        found_working_mem = all_working_mem_by_timeline.get(schedule.timeline, None)

        if found_working_mem:
            if (
                not gen_even_if_not_modified
                and found_working_mem.last_modified_time
                >= working_mem_collection.last_modified_time
            ):
                pass

            # TODO(horia141): should something be done here?

            working_mem = found_working_mem
        else:
            working_mem = WorkingMem.new_working_mem(
                ctx,
                working_mem_collection_ref_id=working_mem_collection.ref_id,
                right_now=today,
                period=working_mem_collection.generation_period,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                working_mem = await uow.get_for(WorkingMem).create(working_mem)
                await progress_reporter.mark_created(working_mem)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                working_mem,
            )

        found_note = all_notes_by_working_mem_ref_id.get(working_mem.ref_id, None)

        if found_note:
            note = found_note
        else:
            note = Note.new_note(
                ctx,
                note_collection_ref_id=note_collection.ref_id,
                domain=NoteDomain.WORKING_MEM,
                source_entity_ref_id=working_mem.ref_id,
                content=[],
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                note = await uow.get_for(Note).create(note)

        found_inbox_task = all_inbox_tasks_by_working_mem_ref_id_and_timeline.get(
            (working_mem.ref_id, schedule.timeline),
            None,
        )

        if found_inbox_task:
            if (
                not gen_even_if_not_modified
                and found_inbox_task.last_modified_time
                >= working_mem.last_modified_time
            ):
                return gen_log_entry

            found_inbox_task = found_inbox_task.update_link_to_working_mem_cleanup(
                ctx,
                project_ref_id=working_mem_collection.cleanup_project_ref_id,
                name=schedule.full_name,
                recurring_timeline=schedule.timeline,
                due_date=schedule.due_date,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.get_for(InboxTask).save(found_inbox_task)
                await progress_reporter.mark_updated(found_inbox_task)
            gen_log_entry = gen_log_entry.add_entity_updated(
                ctx,
                found_inbox_task,
            )
        else:
            inbox_task = InboxTask.new_inbox_task_for_working_mem_cleanup(
                ctx,
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                name=schedule.full_name,
                due_date=schedule.due_date,
                project_ref_id=working_mem_collection.cleanup_project_ref_id,
                working_mem_ref_id=working_mem.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_gen_right_now=today.to_timestamp_at_end_of_day(),
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)
            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_inbox_tasks_for_habit(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
        today: ADate,
        period_filter: frozenset[RecurringTaskPeriod] | None,
        habit: Habit,
        all_inbox_tasks_by_habit_ref_id_and_timeline: dict[
            tuple[EntityId, str],
            list[InboxTask],
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
            habit.gen_params.skip_rule,
            habit.gen_params.actionable_from_day,
            habit.gen_params.actionable_from_month,
            habit.gen_params.due_at_day,
            habit.gen_params.due_at_month,
        )

        if not schedule.should_keep:
            return gen_log_entry

        all_found_tasks_by_repeat_index: dict[int | None, InboxTask] = {
            ft.recurring_repeat_index: ft
            for ft in all_inbox_tasks_by_habit_ref_id_and_timeline.get(
                (habit.ref_id, schedule.timeline),
                [],
            )
        }
        repeat_idx_to_keep: set[int | None] = set()

        task_ranges: Sequence[tuple[ADate | None, ADate]]
        if habit.repeats_in_period_count is not None:
            if habit.repeats_strategy is None:
                raise ValueError("Repeats strategy is not set")
            task_ranges = habit.repeats_strategy.spread_tasks(
                start_date=schedule.first_day,
                end_date=schedule.end_day,
                repeats_in_period=habit.repeats_in_period_count,
            )
        else:
            task_ranges = [(schedule.actionable_date, schedule.due_date)]

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
                    actionable_date=task_ranges[task_idx][0],
                    due_date=task_ranges[task_idx][1],
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    await uow.get_for(InboxTask).save(found_task)
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
                    actionable_date=task_ranges[task_idx][0],
                    due_date=task_ranges[task_idx][1],
                )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    inbox_task = await uow.get_for(InboxTask).create(
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
        period_filter: frozenset[RecurringTaskPeriod] | None,
        all_vacations: list[Vacation],
        chore: Chore,
        all_inbox_tasks_by_chore_ref_id_and_timeline: dict[
            tuple[EntityId, str],
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
            chore.gen_params.skip_rule,
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

        if not schedule.should_keep:
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
                await uow.get_for(InboxTask).save(found_task)
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
                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
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
        period_filter: frozenset[RecurringTaskPeriod] | None,
        metric: Metric,
        collection_params: RecurringTaskGenParams,
        all_inbox_tasks_by_metric_ref_id_and_timeline: dict[
            tuple[EntityId, str],
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
                await uow.get_for(InboxTask).save(found_task)
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
                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
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
        period_filter: frozenset[RecurringTaskPeriod] | None,
        person: Person,
        catch_up_params: RecurringTaskGenParams,
        all_inbox_tasks_by_person_ref_id_and_timeline: dict[
            tuple[EntityId, str],
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
                await uow.get_for(InboxTask).save(found_task)
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
                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry

    async def _generate_birthday_time_event_block_for_person(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        time_event_domain: TimeEventDomain,
        today: ADate,
        person: Person,
        all_birthday_time_event_blocks_by_person_ref_id_and_start_date: dict[
            tuple[EntityId, ADate],
            TimeEventFullDaysBlock,
        ],
        gen_even_if_not_modified: bool,
        gen_log_entry: GenLogEntry,
    ) -> GenLogEntry:
        found_block = (
            all_birthday_time_event_blocks_by_person_ref_id_and_start_date.get(
                (person.ref_id, person.birthday_in_year(today)), None
            )
        )

        if found_block:
            if (
                not gen_even_if_not_modified
                and found_block.last_modified_time >= person.last_modified_time
            ):
                return gen_log_entry

            found_block = found_block.update_for_person_birthday(
                ctx,
                birthday_date=person.birthday_in_year(today),
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.get_for(TimeEventFullDaysBlock).save(found_block)
        else:
            found_block = TimeEventFullDaysBlock.new_time_event_for_person_birthday(
                ctx,
                time_event_domain_ref_id=time_event_domain.ref_id,
                person_ref_id=person.ref_id,
                birthday_date=person.birthday_in_year(today),
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                found_block = await uow.get_for(TimeEventFullDaysBlock).create(
                    found_block
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
        all_inbox_tasks_by_person_ref_id_and_timeline: dict[
            tuple[EntityId, str],
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
            RecurringTaskDueAtDay.build(
                RecurringTaskPeriod.YEARLY,
                birthday.day,
            ),
            RecurringTaskDueAtMonth.build(
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
                await uow.get_for(InboxTask).save(found_task)
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
                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
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
        all_inbox_tasks_by_slack_task_ref_id: dict[EntityId, InboxTask],
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
                await uow.get_for(InboxTask).save(found_task)
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
                await uow.get_for(SlackTask).save(slack_task)
                await progress_reporter.mark_updated(slack_task)

                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
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
        all_inbox_tasks_by_email_task_ref_id: dict[EntityId, InboxTask],
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
                await uow.get_for(InboxTask).save(found_task)
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
                await uow.get_for(EmailTask).save(email_task)
                await progress_reporter.mark_updated(email_task)

                inbox_task = await uow.get_for(InboxTask).create(inbox_task)
                await progress_reporter.mark_created(inbox_task)

            gen_log_entry = gen_log_entry.add_entity_created(
                ctx,
                inbox_task,
            )

        return gen_log_entry
