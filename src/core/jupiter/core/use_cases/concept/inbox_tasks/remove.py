"""The command for removing a inbox task."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivityRespository,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class InboxTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskRemoveArgs, None]
):
    """The command for removing a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.get_for(InboxTask).load_by_id(
            args.ref_id,
            allow_archived=True,
        )

        # Remove time plan activities that are associated with the inbox task.
        # These are entities that just represent the link between a time plan
        # and the inbox task. So they have to go!
        time_plan_activities = await uow.get(
            TimePlanActivityRespository
        ).find_all_generic(
            target=TimePlanActivityTarget.INBOX_TASK,
            target_ref_id=inbox_task.ref_id,
            allow_archived=True,
        )
        for time_plan_activity in time_plan_activities:
            await uow.get(TimePlanActivityRespository).remove(time_plan_activity.ref_id)

        await InboxTaskRemoveService().do_it(
            context.domain_context, uow, progress_reporter, inbox_task
        )
