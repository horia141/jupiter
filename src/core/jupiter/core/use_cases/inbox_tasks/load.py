"""The use case for loading a partcular inbox task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class InboxTaskLoadArgs(UseCaseArgsBase):
    """InboxTaskLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
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


class InboxTaskLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[InboxTaskLoadArgs, InboxTaskLoadResult]
):
    """The use case for loading a particular inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.INBOX_TASKS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskLoadArgs,
    ) -> InboxTaskLoadResult:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.project_repository.load_by_id(inbox_task.project_ref_id)

        if inbox_task.habit_ref_id is not None:
            habit = await uow.habit_repository.load_by_id(inbox_task.habit_ref_id)
        else:
            habit = None

        if inbox_task.chore_ref_id is not None:
            chore = await uow.chore_repository.load_by_id(inbox_task.chore_ref_id)
        else:
            chore = None

        if inbox_task.big_plan_ref_id is not None:
            big_plan = await uow.big_plan_repository.load_by_id(
                inbox_task.big_plan_ref_id
            )
        else:
            big_plan = None

        if inbox_task.metric_ref_id is not None:
            metric = await uow.metric_repository.load_by_id(inbox_task.metric_ref_id)
        else:
            metric = None

        if inbox_task.person_ref_id is not None:
            person = await uow.person_repository.load_by_id(inbox_task.person_ref_id)
        else:
            person = None

        if inbox_task.slack_task_ref_id is not None:
            slack_task = await uow.slack_task_repository.load_by_id(
                inbox_task.slack_task_ref_id
            )
        else:
            slack_task = None

        if inbox_task.email_task_ref_id is not None:
            email_task = await uow.email_task_repository.load_by_id(
                inbox_task.email_task_ref_id
            )
        else:
            email_task = None

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
        )
