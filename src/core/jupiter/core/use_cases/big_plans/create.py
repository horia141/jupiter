"""The command for creating a big plan."""
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.concept.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.projects.project import Project, ProjectRepository
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
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
class BigPlanCreateArgs(UseCaseArgsBase):
    """Big plan create args."""

    name: BigPlanName
    time_plan_ref_id: EntityId | None
    project_ref_id: EntityId | None
    actionable_date: ADate | None
    due_date: ADate | None


@use_case_result
class BigPlanCreateResult(UseCaseResultBase):
    """Big plan create result."""

    new_big_plan: BigPlan
    new_time_plan_activity: TimePlanActivity | None


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanCreateArgs, BigPlanCreateResult]
):
    """The command for creating a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanCreateArgs,
    ) -> BigPlanCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.TIME_PLANS)
            and args.time_plan_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.TIME_PLANS)
        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        time_plan: TimePlan | None = None
        if args.time_plan_ref_id:
            time_plan = await uow.get_for(TimePlan).load_by_id(args.time_plan_ref_id)

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

        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id,
        )

        new_big_plan = BigPlan.new_big_plan(
            context.domain_context,
            big_plan_collection_ref_id=big_plan_collection.ref_id,
            project_ref_id=project_ref_id,
            name=args.name,
            status=BigPlanStatus.ACCEPTED,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
        )
        new_big_plan = await generic_creator(uow, progress_reporter, new_big_plan)

        new_time_plan_activity = None
        if time_plan:
            new_time_plan_activity = TimePlanActivity.new_activity_for_big_plan(
                context.domain_context,
                time_plan_ref_id=time_plan.ref_id,
                big_plan_ref_id=new_big_plan.ref_id,
                kind=TimePlanActivityKind.FINISH,
                feasability=TimePlanActivityFeasability.MUST_DO,
            )
            new_time_plan_activity = await generic_creator(
                uow, progress_reporter, new_time_plan_activity
            )

        return BigPlanCreateResult(
            new_big_plan=new_big_plan, new_time_plan_activity=new_time_plan_activity
        )
