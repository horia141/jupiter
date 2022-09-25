"""The command for creating a habit."""
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class HabitCreateUseCase(AppMutationUseCase["HabitCreateUseCase.Args", None]):
    """The command for creating a habit."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        project_key: Optional[ProjectKey]
        name: HabitName
        period: RecurringTaskPeriod
        eisen: Optional[Eisen]
        difficulty: Optional[Difficulty]
        actionable_from_day: Optional[RecurringTaskDueAtDay]
        actionable_from_month: Optional[RecurringTaskDueAtMonth]
        due_at_time: Optional[RecurringTaskDueAtTime]
        due_at_day: Optional[RecurringTaskDueAtDay]
        due_at_month: Optional[RecurringTaskDueAtMonth]
        skip_rule: Optional[RecurringTaskSkipRule]
        repeats_in_period_count: Optional[int]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        habit_notion_manager: HabitNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with progress_reporter.start_creating_entity(
            "habit", str(args.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                project_collection = uow.project_collection_repository.load_by_parent(
                    workspace.ref_id
                )

                if args.project_key is not None:
                    project = uow.project_repository.load_by_key(
                        project_collection.ref_id, args.project_key
                    )
                    project_ref_id = project.ref_id
                else:
                    project = uow.project_repository.load_by_id(
                        workspace.default_project_ref_id
                    )
                    project_ref_id = workspace.default_project_ref_id

                habit_collection = uow.habit_collection_repository.load_by_parent(
                    workspace.ref_id
                )

                habit = Habit.new_habit(
                    habit_collection_ref_id=habit_collection.ref_id,
                    archived=False,
                    project_ref_id=project_ref_id,
                    name=args.name,
                    gen_params=RecurringTaskGenParams(
                        period=args.period,
                        eisen=args.eisen if args.eisen else Eisen.REGULAR,
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
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )
                habit = uow.habit_repository.create(habit)
                entity_reporter.mark_known_entity_id(habit.ref_id).mark_local_change()

            direct_info = NotionHabit.DirectInfo(
                all_projects_map={project.ref_id: project}
            )
            notion_habit = NotionHabit.new_notion_entity(habit, direct_info)
            self._habit_notion_manager.upsert_leaf(
                habit_collection.ref_id,
                notion_habit,
            )
            entity_reporter.mark_remote_change()
