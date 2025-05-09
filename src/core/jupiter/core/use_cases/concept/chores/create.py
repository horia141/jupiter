"""The command for creating a chore."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_collection import ChoreCollection
from jupiter.core.domain.concept.chores.chore_name import ChoreName
from jupiter.core.domain.concept.projects.project import Project, ProjectRepository
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
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
class ChoreCreateArgs(UseCaseArgsBase):
    """ChoreCreate args."""

    name: ChoreName
    period: RecurringTaskPeriod
    project_ref_id: EntityId | None
    is_key: bool
    eisen: Eisen
    difficulty: Difficulty
    actionable_from_day: RecurringTaskDueAtDay | None
    actionable_from_month: RecurringTaskDueAtMonth | None
    due_at_day: RecurringTaskDueAtDay | None
    due_at_month: RecurringTaskDueAtMonth | None
    must_do: bool
    skip_rule: RecurringTaskSkipRule | None
    start_at_date: ADate | None
    end_at_date: ADate | None


@use_case_result
class ChoreCreateResult(UseCaseResultBase):
    """ChoreCreate result."""

    new_chore: Chore


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreCreateArgs, ChoreCreateResult]
):
    """The command for creating a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreCreateArgs,
    ) -> ChoreCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
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

        new_chore = Chore.new_chore(
            ctx=context.domain_context,
            chore_collection_ref_id=chore_collection.ref_id,
            project_ref_id=project_ref_id,
            name=args.name,
            is_key=args.is_key,
            gen_params=RecurringTaskGenParams(
                period=args.period,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_from_day=args.actionable_from_day,
                actionable_from_month=args.actionable_from_month,
                due_at_day=args.due_at_day,
                due_at_month=args.due_at_month,
                skip_rule=args.skip_rule,
            ),
            start_at_date=args.start_at_date,
            end_at_date=args.end_at_date,
            suspended=False,
            must_do=args.must_do,
        )
        new_chore = await uow.get_for(Chore).create(new_chore)
        await progress_reporter.mark_created(new_chore)

        return ChoreCreateResult(new_chore=new_chore)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreCreateArgs,
        result: ChoreCreateResult,
    ) -> None:
        """Execute the command's post-mutation work."""
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.CHORES],
            period=[args.period],
            filter_chore_ref_ids=[result.new_chore.ref_id],
        )
