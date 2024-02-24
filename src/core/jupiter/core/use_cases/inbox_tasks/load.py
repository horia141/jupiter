"""The use case for loading a partcular inbox task."""
from typing import Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
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
    habit: Optional[Habit] = None
    chore: Optional[Chore] = None
    big_plan: Optional[BigPlan] = None
    metric: Optional[Metric] = None
    person: Optional[Person] = None
    slack_task: Optional[SlackTask] = None
    email_task: Optional[EmailTask] = None
    note: Optional[Note] = None


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
        inbox_task = await uow.repository_for(InboxTask).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.repository_for(Project).load_by_id(inbox_task.project_ref_id)

        if inbox_task.habit_ref_id is not None:
            habit = await uow.repository_for(Habit).load_by_id(inbox_task.habit_ref_id)
        else:
            habit = None

        if inbox_task.chore_ref_id is not None:
            chore = await uow.repository_for(Chore).load_by_id(inbox_task.chore_ref_id)
        else:
            chore = None

        if inbox_task.big_plan_ref_id is not None:
            big_plan = await uow.repository_for(BigPlan).load_by_id(
                inbox_task.big_plan_ref_id
            )
        else:
            big_plan = None

        if inbox_task.metric_ref_id is not None:
            metric = await uow.repository_for(Metric).load_by_id(inbox_task.metric_ref_id)
        else:
            metric = None

        if inbox_task.person_ref_id is not None:
            person = await uow.repository_for(Person).load_by_id(inbox_task.person_ref_id)
        else:
            person = None

        if inbox_task.slack_task_ref_id is not None:
            slack_task = await uow.repository_for(SlackTask).load_by_id(
                inbox_task.slack_task_ref_id
            )
        else:
            slack_task = None

        if inbox_task.email_task_ref_id is not None:
            email_task = await uow.repository_for(EmailTask).load_by_id(
                inbox_task.email_task_ref_id
            )
        else:
            email_task = None

        note = await uow.repository_for(Note).load_optional_for_source(
            NoteDomain.INBOX_TASK,
            inbox_task.ref_id,
            allow_archived=args.allow_archived,
        )

        return InboxTaskLoadResult(
            inbox_task=inbox_task,
            project=project,
            habit=habit,
            chore=chore,
            big_plan=big_plan,
            metric=metric,
            person=person,
            slack_task=slack_task,
            email_task=email_task,
            note=note,
        )
