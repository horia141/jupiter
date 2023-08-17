"""The command for associating a inbox task with a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class InboxTaskAssociateWithBigPlanArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    big_plan_ref_id: Optional[EntityId] = None


class InboxTaskAssociateWithBigPlanUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskAssociateWithBigPlanArgs, None],
):
    """The command for associating a inbox task with a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return (WorkspaceFeature.INBOX_TASKS, WorkspaceFeature.BIG_PLANS)

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskAssociateWithBigPlanArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)

        try:
            if args.big_plan_ref_id:
                big_plan = await uow.big_plan_repository.load_by_id(
                    args.big_plan_ref_id,
                )
                inbox_task = inbox_task.associate_with_big_plan(
                    project_ref_id=big_plan.project_ref_id,
                    big_plan_ref_id=args.big_plan_ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
            else:
                inbox_task = inbox_task.release_from_big_plan(
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifying a generated task's field {err.field} is not possible",
            ) from err

        await uow.inbox_task_repository.save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)
