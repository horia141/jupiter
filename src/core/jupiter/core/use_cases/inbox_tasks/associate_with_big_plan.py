"""The command for associating a inbox task with a big plan."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import (
    CannotModifyGeneratedTaskError,
    InboxTask,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class InboxTaskAssociateWithBigPlanArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    big_plan_ref_id: EntityId | None = None


@mutation_use_case([WorkspaceFeature.INBOX_TASKS, WorkspaceFeature.BIG_PLANS])
class InboxTaskAssociateWithBigPlanUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskAssociateWithBigPlanArgs, None],
):
    """The command for associating a inbox task with a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskAssociateWithBigPlanArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.get_for(InboxTask).load_by_id(args.ref_id)

        try:
            if args.big_plan_ref_id:
                big_plan = await uow.get_for(BigPlan).load_by_id(
                    args.big_plan_ref_id,
                )
                inbox_task = inbox_task.associate_with_big_plan(
                    ctx=context.domain_context,
                    project_ref_id=big_plan.project_ref_id,
                    big_plan_ref_id=args.big_plan_ref_id,
                )
            else:
                inbox_task = inbox_task.release_from_big_plan(
                    ctx=context.domain_context,
                )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifying a generated task's field {err.field} is not possible",
            ) from err

        await uow.get_for(InboxTask).save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)
