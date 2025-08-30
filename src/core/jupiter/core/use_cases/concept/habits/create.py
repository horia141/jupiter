"""The command for creating a habit."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_collection import HabitCollection
from jupiter.core.domain.concept.habits.habit_name import HabitName
from jupiter.core.domain.concept.habits.habit_repeats_strategy import (
    HabitRepeatsStrategy,
)
from jupiter.core.domain.concept.projects.project import Project, ProjectRepository
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
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
class HabitCreateArgs(UseCaseArgsBase):
    """HabitCreate args.."""

    name: HabitName
    period: RecurringTaskPeriod
    project_ref_id: EntityId | None
    is_key: bool
    eisen: Eisen
    difficulty: Difficulty
    actionable_from_day: RecurringTaskDueAtDay | None
    actionable_from_month: RecurringTaskDueAtMonth | None
    due_at_day: RecurringTaskDueAtDay | None
    due_at_month: RecurringTaskDueAtMonth | None
    skip_rule: RecurringTaskSkipRule | None
    repeats_strategy: HabitRepeatsStrategy | None
    repeats_in_period_count: int | None


@use_case_result
class HabitCreateResult(UseCaseResultBase):
    """HabitCreate result."""

    new_habit: Habit


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitCreateArgs, HabitCreateResult]
):
    """The command for creating a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitCreateArgs,
    ) -> HabitCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.project_ref_id is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
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

        new_habit = Habit.new_habit(
            ctx=context.domain_context,
            habit_collection_ref_id=habit_collection.ref_id,
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
            suspended=False,
            repeats_strategy=args.repeats_strategy,
            repeats_in_period_count=args.repeats_in_period_count,
        )
        new_habit = await uow.get_for(Habit).create(new_habit)
        await progress_reporter.mark_created(new_habit)

        return HabitCreateResult(new_habit=new_habit)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitCreateArgs,
        result: HabitCreateResult,
    ) -> None:
        """Execute the command's post-mutation work."""
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.HABITS],
            period=[args.period],
            filter_habit_ref_ids=[result.new_habit.ref_id],
        )
