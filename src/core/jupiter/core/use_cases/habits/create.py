"""The command for creating a habit."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class HabitCreateArgs(UseCaseArgsBase):
    """HabitCreate args.."""

    name: HabitName
    period: RecurringTaskPeriod
    project_ref_id: Optional[EntityId] = None
    eisen: Optional[Eisen] = None
    difficulty: Optional[Difficulty] = None
    actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    due_at_time: Optional[RecurringTaskDueAtTime] = None
    due_at_day: Optional[RecurringTaskDueAtDay] = None
    due_at_month: Optional[RecurringTaskDueAtMonth] = None
    skip_rule: Optional[RecurringTaskSkipRule] = None
    repeats_in_period_count: Optional[int] = None


@dataclass
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

        habit_collection = await uow.habit_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        new_habit = Habit.new_habit(
            ctx=context.domain_context,
            habit_collection_ref_id=habit_collection.ref_id,
            project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
            name=args.name,
            gen_params=RecurringTaskGenParams(
                period=args.period,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_from_day=args.actionable_from_day,
                actionable_from_month=args.actionable_from_month,
                due_at_time=args.due_at_time,
                due_at_day=args.due_at_day,
                due_at_month=args.due_at_month,
            ),
            skip_rule=args.skip_rule,
            suspended=False,
            repeats_in_period_count=args.repeats_in_period_count,
        )
        new_habit = await uow.habit_repository.create(new_habit)
        await progress_reporter.mark_created(new_habit)

        return HabitCreateResult(new_habit=new_habit)
