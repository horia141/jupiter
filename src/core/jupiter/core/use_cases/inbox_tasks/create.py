"""The command for creating a inbox task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import FeatureUnavailableError, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class InboxTaskCreateArgs(UseCaseArgsBase):
    """InboxTaskCreate args."""

    name: InboxTaskName
    project_ref_id: Optional[EntityId] = None
    big_plan_ref_id: Optional[EntityId] = None
    eisen: Optional[Eisen] = None
    difficulty: Optional[Difficulty] = None
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None


@dataclass
class InboxTaskCreateResult(UseCaseResultBase):
    """InboxTaskCreate result."""

    new_inbox_task: InboxTask


class InboxTaskCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskCreateArgs, InboxTaskCreateResult],
):
    """The command for creating a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.INBOX_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskCreateArgs,
    ) -> InboxTaskCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.BIG_PLANS)
            and args.big_plan_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.BIG_PLANS)

        big_plan: Optional[BigPlan] = None
        if args.big_plan_ref_id:
            big_plan = await uow.big_plan_repository.load_by_id(
                args.big_plan_ref_id,
            )

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )

        new_inbox_task = InboxTask.new_inbox_task(
            inbox_task_collection_ref_id=inbox_task_collection.ref_id,
            archived=False,
            name=args.name,
            status=InboxTaskStatus.ACCEPTED,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
            big_plan=big_plan,
            eisen=args.eisen,
            difficulty=args.difficulty,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )

        new_inbox_task = await uow.inbox_task_repository.create(new_inbox_task)
        await progress_reporter.mark_created(new_inbox_task)

        return InboxTaskCreateResult(new_inbox_task=new_inbox_task)
