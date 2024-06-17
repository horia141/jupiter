"""Use case for archiving a time plan activity."""
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.infra.generic_archiver import generic_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
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
class TimePlanActivityArchiveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanActivityArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[TimePlanActivityArchiveArgs, None]
):
    """Use case for archiving a time plan activity."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanActivityArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        activity = await uow.get_for(TimePlanActivity).load_by_id(args.ref_id)

        if activity.target == TimePlanActivityTarget.BIG_PLAN:
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(workspace.ref_id)
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=InboxTaskSource.BIG_PLAN,
                big_plan_ref_id=activity.target_ref_id,
            )
            if len(inbox_tasks) > 0:
                inbox_task_activities = await uow.get_for(
                    TimePlanActivity
                ).find_all_generic(
                    parent_ref_id=activity.parent_ref_id,
                    allow_archived=False,
                    target=TimePlanActivityTarget.INBOX_TASK,
                    target_ref_id=[it.ref_id for it in inbox_tasks],
                )
                for inbox_task_activity in inbox_task_activities:
                    await generic_archiver(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        TimePlanActivity,
                        inbox_task_activity.ref_id,
                    )

        await generic_archiver(
            context.domain_context,
            uow,
            progress_reporter,
            TimePlanActivity,
            args.ref_id,
        )
