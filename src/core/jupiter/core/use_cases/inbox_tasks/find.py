"""The command for finding a inbox task."""
from collections import defaultdict

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
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


@use_case_args
class InboxTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    filter_just_workable: bool | None
    filter_ref_ids: list[EntityId] | None
    filter_project_ref_ids: list[EntityId] | None
    filter_sources: list[InboxTaskSource] | None


@use_case_result_part
class InboxTaskFindResultEntry(UseCaseResultBase):
    """A single entry in the load all inbox tasks response."""

    inbox_task: InboxTask
    note: Note | None
    project: Project
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
        filter_sources = workspace.infer_sources_for_enabled_features(
            args.filter_sources
        )

        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
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
        )

        habits = await uow.get_for(Habit).find_all(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.habit_ref_id for it in inbox_tasks if it.habit_ref_id is not None
            ),
        )
        habits_by_ref_id = {rt.ref_id: rt for rt in habits}

        chores = await uow.get_for(Chore).find_all(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.chore_ref_id for it in inbox_tasks if it.chore_ref_id is not None
            ),
        )
        chores_by_ref_id = {rt.ref_id: rt for rt in chores}

        big_plans = await uow.get_for(BigPlan).find_all(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.big_plan_ref_id
                for it in inbox_tasks
                if it.big_plan_ref_id is not None
            ),
        )
        big_plans_by_ref_id = {bp.ref_id: bp for bp in big_plans}

        metrics = await uow.get_for(Metric).find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.metric_ref_id for it in inbox_tasks if it.metric_ref_id is not None
            ),
        )
        metrics_by_ref_id = {m.ref_id: m for m in metrics}

        persons = await uow.get_for(Person).find_all(
            parent_ref_id=person_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.person_ref_id for it in inbox_tasks if it.person_ref_id is not None
            ),
        )
        persons_by_ref_id = {p.ref_id: p for p in persons}

        slack_tasks = await uow.get_for(SlackTask).find_all(
            parent_ref_id=slack_task_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.slack_task_ref_id
                for it in inbox_tasks
                if it.slack_task_ref_id is not None
            ),
        )
        slack_tasks_by_ref_id = {p.ref_id: p for p in slack_tasks}

        email_tasks = await uow.get_for(EmailTask).find_all(
            parent_ref_id=email_task_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=(
                it.email_task_ref_id
                for it in inbox_tasks
                if it.email_task_ref_id is not None
            ),
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

        return InboxTaskFindResult(
            entries=[
                InboxTaskFindResultEntry(
                    inbox_task=it,
                    project=project_by_ref_id[it.project_ref_id],
                    habit=habits_by_ref_id[it.habit_ref_id]
                    if it.habit_ref_id is not None
                    else None,
                    chore=chores_by_ref_id[it.chore_ref_id]
                    if it.chore_ref_id is not None
                    else None,
                    big_plan=big_plans_by_ref_id[it.big_plan_ref_id]
                    if it.big_plan_ref_id is not None
                    else None,
                    metric=metrics_by_ref_id[it.metric_ref_id]
                    if it.metric_ref_id is not None
                    else None,
                    person=persons_by_ref_id[it.person_ref_id]
                    if it.person_ref_id is not None
                    else None,
                    slack_task=slack_tasks_by_ref_id[it.slack_task_ref_id]
                    if it.slack_task_ref_id is not None
                    else None,
                    email_task=email_tasks_by_ref_id[it.email_task_ref_id]
                    if it.email_task_ref_id is not None
                    else None,
                    note=notes_by_inbox_task_ref_id.get(it.ref_id, None),
                )
                for it in inbox_tasks
            ],
        )
