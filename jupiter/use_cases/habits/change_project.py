"""The command for changing the project for a habit."""
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain import schedules
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
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
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider


class HabitChangeProjectUseCase(
    AppMutationUseCase["HabitChangeProjectUseCase.Args", None]
):
    """The command for changing the project of a habit."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId
        project_key: Optional[ProjectKey]

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        habit_notion_manager: HabitNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
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

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )

            if args.project_key:
                project = uow.project_repository.load_by_key(
                    project_collection.ref_id, args.project_key
                )
            else:
                project = uow.project_repository.load_by_id(
                    workspace.default_project_ref_id
                )

            habit = uow.habit_repository.load_by_id(args.ref_id)

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            all_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=[args.ref_id],
            )

        for inbox_task in all_inbox_tasks:
            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    schedule = schedules.get_schedule(
                        habit.gen_params.period,
                        habit.name,
                        cast(Timestamp, inbox_task.recurring_gen_right_now),
                        self._global_properties.timezone,
                        habit.skip_rule,
                        habit.gen_params.actionable_from_day,
                        habit.gen_params.actionable_from_month,
                        habit.gen_params.due_at_time,
                        habit.gen_params.due_at_day,
                        habit.gen_params.due_at_month,
                    )

                    inbox_task = inbox_task.update_link_to_habit(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        timeline=schedule.timeline,
                        repeat_index=inbox_task.recurring_repeat_index,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        eisen=habit.gen_params.eisen,
                        difficulty=habit.gen_params.difficulty,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(inbox_task.name))

                    uow.inbox_task_repository.save(inbox_task)
                    entity_reporter.mark_local_change()

                inbox_task_direct_info = NotionInboxTask.DirectInfo(
                    all_projects_map={project.ref_id: project}, all_big_plans_map={}
                )
                notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                notion_inbox_task = notion_inbox_task.join_with_entity(
                    inbox_task, inbox_task_direct_info
                )
                self._inbox_task_notion_manager.save_leaf(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task
                )
                entity_reporter.mark_remote_change()

        with progress_reporter.start_updating_entity(
            "habit", args.ref_id, str(habit.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                habit = habit.change_project(
                    project_ref_id=project.ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                uow.habit_repository.save(habit)
                entity_reporter.mark_local_change()

            habit_direct_info = NotionHabit.DirectInfo(
                all_projects_map={project.ref_id: project}
            )

            notion_habit = self._habit_notion_manager.load_leaf(
                habit.habit_collection_ref_id, habit.ref_id
            )
            notion_habit = notion_habit.join_with_entity(habit, habit_direct_info)
            self._habit_notion_manager.save_leaf(
                habit.habit_collection_ref_id, notion_habit
            )
            entity_reporter.mark_remote_change()
