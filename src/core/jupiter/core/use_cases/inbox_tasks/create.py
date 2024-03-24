"""The command for creating a inbox task."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.projects.project import Project, ProjectRepository
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class InboxTaskCreateArgs(UseCaseArgsBase):
    """InboxTaskCreate args."""

    name: InboxTaskName
    project_ref_id: EntityId | None
    big_plan_ref_id: EntityId | None
    eisen: Eisen | None
    difficulty: Difficulty | None
    actionable_date: ADate | None
    due_date: ADate | None


@use_case_result
class InboxTaskCreateResult(UseCaseResultBase):
    """InboxTaskCreate result."""

    new_inbox_task: InboxTask


@mutation_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskCreateArgs, InboxTaskCreateResult],
):
    """The command for creating a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
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

        big_plan: BigPlan | None = None
        if args.big_plan_ref_id:
            big_plan = await uow.get_for(BigPlan).load_by_id(
                args.big_plan_ref_id,
            )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        if args.project_ref_id is None:
            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id,
            )
            root_project = await uow.get(ProjectRepository).load_root_project(
                project_collection.ref_id
            )
            project_ref_id = root_project.ref_id
        else:
            await uow.get_for(Project).load_by_id(args.project_ref_id)
            project_ref_id = args.project_ref_id

        new_inbox_task = InboxTask.new_inbox_task(
            ctx=context.domain_context,
            inbox_task_collection_ref_id=inbox_task_collection.ref_id,
            name=args.name,
            status=InboxTaskStatus.ACCEPTED,
            project_ref_id=project_ref_id,
            eisen=args.eisen,
            difficulty=args.difficulty,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
            big_plan_ref_id=big_plan.ref_id if big_plan else None,
            big_plan_project_ref_id=big_plan.project_ref_id if big_plan else None,
            big_plan_actionable_date=big_plan.actionable_date if big_plan else None,
            big_plan_due_date=big_plan.due_date if big_plan else None,
        )

        new_inbox_task = await uow.get_for(InboxTask).create(new_inbox_task)
        await progress_reporter.mark_created(new_inbox_task)

        return InboxTaskCreateResult(new_inbox_task=new_inbox_task)
