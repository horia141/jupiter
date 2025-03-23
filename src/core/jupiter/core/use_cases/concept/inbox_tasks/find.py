"""The command for finding a inbox task."""

from collections import defaultdict

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_collection import ChoreCollection
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_collection import HabitCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.persons.person import Person
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
from jupiter.core.domain.concept.working_mem.working_mem import WorkingMem
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)
from sqlalchemy import select, text


@use_case_args
class InboxTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    include_time_event_blocks: bool
    filter_just_workable: bool | None
    filter_just_generated: bool | None
    filter_ref_ids: list[EntityId] | None
    filter_project_ref_ids: list[EntityId] | None
    filter_sources: list[InboxTaskSource] | None
    filter_source_entity_ref_ids: list[EntityId] | None


@use_case_result_part
class InboxTaskFindResultEntry(UseCaseResultBase):
    """A single entry in the load all inbox tasks response."""

    inbox_task: InboxTask
    note: Note | None
    project: Project
    time_event_blocks: list[TimeEventInDayBlock] | None
    working_mem: WorkingMem | None
    habit: Habit | None
    chore: Chore | None
    big_plan: BigPlan | None
    metric: Metric | None
    person: Person | None
    slack_task: SlackTask | None
    email_task: EmailTask | None


@use_case_result
class InboxTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    entries: list[InboxTaskFindResultEntry]


@readonly_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[InboxTaskFindArgs, InboxTaskFindResult]
):
    """The command for finding a inbox task."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: InboxTaskFindArgs,
    ) -> InboxTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        filter_sources = (
            args.filter_sources
            if args.filter_sources is not None
            else workspace.infer_sources_for_enabled_features(None)
        )
        if args.filter_just_generated:
            filter_sources = self._filter_sources_for_generated_tasks(filter_sources)

        big_diff = list(
            set(filter_sources).difference(
                workspace.infer_sources_for_enabled_features(filter_sources)
            )
        )
        if len(big_diff) > 0:
            raise FeatureUnavailableError(
                f"Sources {','.join(s.value for s in big_diff)} are not supported in this workspace"
            )

        filter_status: list[InboxTaskStatus] | NoFilter = (
            InboxTaskStatus.all_workable_statuses()
            if args.filter_just_workable
            else NoFilter()
        )
        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id
        )
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id,
        )
        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
            workspace.ref_id,
        )
        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id,
        )
        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        push_integrations_group = await uow.get_for(
            PushIntegrationGroup
        ).load_by_parent(
            workspace.ref_id,
        )
        slack_task_collection = await uow.get_for(SlackTaskCollection).load_by_parent(
            push_integrations_group.ref_id,
        )
        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_parent(
            push_integrations_group.ref_id,
        )

        projects = await uow.get_for(Project).find_all_generic(
            parent_ref_id=project_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_project_ref_ids or NoFilter(),
        )
        project_by_ref_id = {p.ref_id: p for p in projects}

        inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
            status=filter_status,
            source=filter_sources,
            project_ref_id=args.filter_project_ref_ids or NoFilter(),
            source_entity_ref_id=args.filter_source_entity_ref_ids or NoFilter(),
        )

        working_mems = await uow.get_for(WorkingMem).find_all(
            parent_ref_id=working_mem_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.WORKING_MEM_CLEANUP
            ],
        )
        working_mems_by_ref_id = {wm.ref_id: wm for wm in working_mems}

        habits = await uow.get_for(Habit).find_all(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.HABIT
            ],
        )
        habits_by_ref_id = {rt.ref_id: rt for rt in habits}

        chores = await uow.get_for(Chore).find_all(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.CHORE
            ],
        )
        chores_by_ref_id = {rt.ref_id: rt for rt in chores}

        big_plans = await uow.get_for(BigPlan).find_all(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.BIG_PLAN
            ],
        )
        big_plans_by_ref_id = {bp.ref_id: bp for bp in big_plans}

        metrics = await uow.get_for(Metric).find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.METRIC
            ],
        )
        metrics_by_ref_id = {m.ref_id: m for m in metrics}

        persons = await uow.get_for(Person).find_all(
            parent_ref_id=person_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source
                in {InboxTaskSource.PERSON_BIRTHDAY, InboxTaskSource.PERSON_CATCH_UP}
            ],
        )
        persons_by_ref_id = {p.ref_id: p for p in persons}

        slack_tasks = await uow.get_for(SlackTask).find_all(
            parent_ref_id=slack_task_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.SLACK_TASK
            ],
        )
        slack_tasks_by_ref_id = {p.ref_id: p for p in slack_tasks}

        email_tasks = await uow.get_for(EmailTask).find_all(
            parent_ref_id=email_task_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                it.source_entity_ref_id_for_sure
                for it in inbox_tasks
                if it.source == InboxTaskSource.EMAIL_TASK
            ],
        )
        email_tasks_by_ref_id = {p.ref_id: p for p in email_tasks}

        notes_by_inbox_task_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.INBOX_TASK,
                allow_archived=True,
                source_entity_ref_id=[it.ref_id for it in inbox_tasks],
            )
            for note in notes:
                notes_by_inbox_task_ref_id[note.source_entity_ref_id] = note

        time_event_blocks_by_inbox_task_ref_id: defaultdict[
            EntityId, list[TimeEventInDayBlock]
        ] = defaultdict(list)
        if args.include_time_event_blocks:
            time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
                workspace.ref_id
            )
            time_event_blocks = await uow.get_for(TimeEventInDayBlock).find_all_generic(
                parent_ref_id=time_event_domain.ref_id,
                allow_archived=True,
                namespace=TimeEventNamespace.INBOX_TASK,
                source_entity_ref_id=[it.ref_id for it in inbox_tasks],
            )
            for block in time_event_blocks:
                time_event_blocks_by_inbox_task_ref_id[
                    block.source_entity_ref_id
                ].append(block)

        return InboxTaskFindResult(
            entries=[
                InboxTaskFindResultEntry(
                    inbox_task=it,
                    project=project_by_ref_id[it.project_ref_id],
                    working_mem=(
                        working_mems_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.WORKING_MEM_CLEANUP
                        else None
                    ),
                    habit=(
                        habits_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.HABIT
                        else None
                    ),
                    chore=(
                        chores_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.CHORE
                        else None
                    ),
                    big_plan=(
                        big_plans_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.BIG_PLAN
                        else None
                    ),
                    metric=(
                        metrics_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.METRIC
                        else None
                    ),
                    person=(
                        persons_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.PERSON_BIRTHDAY
                        or it.source == InboxTaskSource.PERSON_CATCH_UP
                        else None
                    ),
                    slack_task=(
                        slack_tasks_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.SLACK_TASK
                        else None
                    ),
                    email_task=(
                        email_tasks_by_ref_id[it.source_entity_ref_id_for_sure]
                        if it.source == InboxTaskSource.EMAIL_TASK
                        else None
                    ),
                    note=notes_by_inbox_task_ref_id.get(it.ref_id, None),
                    time_event_blocks=time_event_blocks_by_inbox_task_ref_id.get(
                        it.ref_id, None
                    ),
                )
                for it in inbox_tasks
            ],
        )

    def _filter_sources_for_generated_tasks(
        self, sources: list[InboxTaskSource]
    ) -> list[InboxTaskSource]:
        return [s for s in sources if not s.allow_user_changes]
