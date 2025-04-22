"""The use case for loading a partcular inbox task."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.concept.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.working_mem.working_mem import WorkingMem
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class InboxTaskLoadArgs(UseCaseArgsBase):
    """InboxTaskLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class InboxTaskLoadResult(UseCaseResultBase):
    """InboxTaskLoadResult."""

    inbox_task: InboxTask
    project: Project
    working_mem: WorkingMem | None
    time_plan: TimePlan | None
    habit: Habit | None
    chore: Chore | None
    big_plan: BigPlan | None
    metric: Metric | None
    person: Person | None
    slack_task: SlackTask | None
    email_task: EmailTask | None
    note: Note | None
    time_event_blocks: list[TimeEventInDayBlock]


@readonly_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[InboxTaskLoadArgs, InboxTaskLoadResult]
):
    """The use case for loading a particular inbox task."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: InboxTaskLoadArgs,
    ) -> InboxTaskLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id
        )
        inbox_task = await uow.get_for(InboxTask).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.get_for(Project).load_by_id(inbox_task.project_ref_id)

        if inbox_task.source is InboxTaskSource.WORKING_MEM_CLEANUP:
            working_mem = await uow.get_for(WorkingMem).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            working_mem = None

        if inbox_task.source is InboxTaskSource.TIME_PLAN:
            time_plan = await uow.get_for(TimePlan).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            time_plan = None

        if inbox_task.source is InboxTaskSource.HABIT:
            habit = await uow.get_for(Habit).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            habit = None

        if inbox_task.source is InboxTaskSource.CHORE:
            chore = await uow.get_for(Chore).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            chore = None

        if inbox_task.source is InboxTaskSource.BIG_PLAN:
            big_plan = await uow.get_for(BigPlan).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            big_plan = None

        if inbox_task.source is InboxTaskSource.METRIC:
            metric = await uow.get_for(Metric).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            metric = None

        if (
            inbox_task.source is InboxTaskSource.PERSON_BIRTHDAY
            or inbox_task.source is InboxTaskSource.PERSON_CATCH_UP
        ):
            person = await uow.get_for(Person).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            person = None

        if inbox_task.source is InboxTaskSource.SLACK_TASK:
            slack_task = await uow.get_for(SlackTask).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            slack_task = None

        if inbox_task.source is InboxTaskSource.EMAIL_TASK:
            email_task = await uow.get_for(EmailTask).load_by_id(
                inbox_task.source_entity_ref_id_for_sure, allow_archived=True
            )
        else:
            email_task = None

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.INBOX_TASK,
            inbox_task.ref_id,
            allow_archived=args.allow_archived,
        )
        time_event_blocks = await uow.get_for(TimeEventInDayBlock).find_all_generic(
            parent_ref_id=time_event_domain.ref_id,
            allow_archived=False,
            namespace=TimeEventNamespace.INBOX_TASK,
            source_entity_ref_id=[inbox_task.ref_id],
        )

        return InboxTaskLoadResult(
            inbox_task=inbox_task,
            project=project,
            working_mem=working_mem,
            time_plan=time_plan,
            habit=habit,
            chore=chore,
            big_plan=big_plan,
            metric=metric,
            person=person,
            slack_task=slack_task,
            email_task=email_task,
            note=note,
            time_event_blocks=time_event_blocks,
        )
