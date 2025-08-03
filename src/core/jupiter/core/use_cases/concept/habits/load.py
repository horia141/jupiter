"""Use case for loading a particular habit."""

from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_streak_mark import (
    HabitStreakMark,
    HabitStreakMarkRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class HabitLoadArgs(UseCaseArgsBase):
    """HabitLoadArgs."""

    ref_id: EntityId
    allow_archived: bool
    inbox_task_retrieve_offset: int | None
    include_streak_marks_earliest_date: ADate | None
    include_streak_marks_latest_date: ADate | None


@use_case_result
class HabitLoadResult(UseCaseResultBase):
    """HabitLoadResult."""

    habit: Habit
    project: Project
    inbox_tasks: list[InboxTask]
    inbox_tasks_total_cnt: int
    inbox_tasks_page_size: int
    streak_marks: list[HabitStreakMark]
    streak_mark_earliest_date: ADate
    streak_mark_latest_date: ADate
    note: Note | None


@readonly_use_case(WorkspaceFeature.HABITS)
class HabitLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HabitLoadArgs, HabitLoadResult]
):
    """Use case for loading a particular habit."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: HabitLoadArgs,
    ) -> HabitLoadResult:
        """Execute the command's action."""
        if (
            args.inbox_task_retrieve_offset is not None
            and args.inbox_task_retrieve_offset < 0
        ):
            raise InputValidationError("Invalid inbox_task_retrieve_offset")
        if (
            args.include_streak_marks_earliest_date is not None
            and args.include_streak_marks_latest_date is not None
            and args.include_streak_marks_earliest_date
            > args.include_streak_marks_latest_date
        ):
            raise InputValidationError(
                "Invalid streak_mark_earliest_date or streak_mark_latest_date"
            )

        workspace = context.workspace
        habit = await uow.get_for(Habit).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.get_for(Project).load_by_id(habit.project_ref_id)
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        inbox_tasks_total_cnt = await uow.get(InboxTaskRepository).count_all_for_source(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=args.allow_archived,
            source=InboxTaskSource.HABIT,
            source_entity_ref_id=habit.ref_id,
        )
        inbox_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.HABIT,
            source_entity_ref_id=habit.ref_id,
            retrieve_offset=args.inbox_task_retrieve_offset or 0,
            retrieve_limit=InboxTaskRepository.PAGE_SIZE,
        )

        streak_mark_earliest_date = (
            args.include_streak_marks_earliest_date
            or self._time_provider.get_current_date().subtract_days(365)
        )
        streak_mark_latest_date = (
            args.include_streak_marks_latest_date
            or self._time_provider.get_current_date()
        )

        streak_marks = await uow.get(HabitStreakMarkRepository).find_all_between_dates(
            habit.ref_id,
            streak_mark_earliest_date,
            streak_mark_latest_date,
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.HABIT,
            habit.ref_id,
            allow_archived=args.allow_archived,
        )

        return HabitLoadResult(
            habit=habit,
            project=project,
            inbox_tasks=inbox_tasks,
            inbox_tasks_total_cnt=inbox_tasks_total_cnt,
            inbox_tasks_page_size=InboxTaskRepository.PAGE_SIZE,
            streak_marks=streak_marks,
            streak_mark_earliest_date=streak_mark_earliest_date,
            streak_mark_latest_date=streak_mark_latest_date,
            note=note,
        )
