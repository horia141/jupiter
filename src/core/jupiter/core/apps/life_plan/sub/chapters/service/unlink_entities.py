"""A service for unlinking a chapter from associated entities."""

from jupiter.core.apps.big_plans.collection import BigPlanCollection
from jupiter.core.apps.big_plans.root import BigPlan
from jupiter.core.apps.chores.collection import ChoreCollection
from jupiter.core.apps.chores.root import Chore
from jupiter.core.apps.chores.sub.stack.root import ChoreStack
from jupiter.core.apps.habits.collection import HabitCollection
from jupiter.core.apps.habits.sub.habit.root import Habit
from jupiter.core.apps.habits.sub.stack.root import HabitStack
from jupiter.core.apps.life_plan.root import LifePlan
from jupiter.core.apps.life_plan.sub.chapters.root import Chapter
from jupiter.core.apps.time_plans.life_plan_links import (
    TimePlanChapterLinkRepository,
)
from jupiter.core.apps.todo.domain import TodoDomain
from jupiter.core.apps.todo.root import TodoTask
from jupiter.framework.context import DomainContext
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.update_action import UpdateAction


class ChapterUnlinkEntitiesService:
    """A service for unlinking a chapter from associated entities."""

    async def unlink_entities(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        life_plan: LifePlan,
        chapter: Chapter,
    ) -> None:
        """Unlink the chapter from associated big plans, chores, and habits."""
        # Unlink from TodoTasks
        todo_task_collection = await uow.get_for(TodoDomain).load_by_parent(
            life_plan.workspace.ref_id
        )
        todo_tasks = await uow.get_for(TodoTask).find_all_generic(
            parent_ref_id=todo_task_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for todo_task in todo_tasks:
            updated_todo_task = todo_task.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
                scheduling_params=UpdateAction.do_nothing(),
            )
            await uow.get_for(TodoTask).save(updated_todo_task)

        # Unlink from BigPlans
        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            life_plan.workspace.ref_id
        )
        big_plans = await uow.get_for(BigPlan).find_all_generic(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for big_plan in big_plans:
            updated_big_plan = big_plan.update(
                ctx,
                name=UpdateAction.do_nothing(),
                status=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
                is_key=UpdateAction.do_nothing(),
                eisen=UpdateAction.do_nothing(),
                difficulty=UpdateAction.do_nothing(),
                actionable_date=UpdateAction.do_nothing(),
                due_date=UpdateAction.do_nothing(),
                dependency_ref_ids=UpdateAction.do_nothing(),
                scheduling_params=UpdateAction.do_nothing(),
            )
            await uow.get_for(BigPlan).save(updated_big_plan)
            await progress_reporter.mark_updated(updated_big_plan)

        # Unlink from Chores
        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
            life_plan.workspace.ref_id
        )
        chores = await uow.get_for(Chore).find_all_generic(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for chore in chores:
            updated_chore = chore.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
                stack_ref_id=UpdateAction.do_nothing(),
                is_key=UpdateAction.do_nothing(),
                gen_params=UpdateAction.do_nothing(),
                start_at_date=UpdateAction.do_nothing(),
                end_at_date=UpdateAction.do_nothing(),
                suspended=UpdateAction.do_nothing(),
                must_do=UpdateAction.do_nothing(),
                scheduling_params=UpdateAction.do_nothing(),
            )
            await uow.get_for(Chore).save(updated_chore)
            await progress_reporter.mark_updated(updated_chore)

        chore_stacks = await uow.get_for(ChoreStack).find_all_generic(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for stack in chore_stacks:
            updated_stack = stack.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
            )
            await uow.get_for(ChoreStack).save(updated_stack)
            await progress_reporter.mark_updated(updated_stack)

        # Unlink from Habits
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            life_plan.workspace.ref_id
        )
        habits = await uow.get_for(Habit).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for habit in habits:
            updated_habit = habit.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
                stack_ref_id=UpdateAction.do_nothing(),
                is_key=UpdateAction.do_nothing(),
                gen_params=UpdateAction.do_nothing(),
                repeats_in_period_count=UpdateAction.do_nothing(),
                suspended=UpdateAction.do_nothing(),
                repeats_strategy=UpdateAction.do_nothing(),
                scheduling_params=UpdateAction.do_nothing(),
            )
            await uow.get_for(Habit).save(updated_habit)
            await progress_reporter.mark_updated(updated_habit)

        habit_stacks = await uow.get_for(HabitStack).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            chapter_ref_id=chapter.ref_id,
        )
        for habit_stack in habit_stacks:
            updated_habit_stack = habit_stack.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.do_nothing(),
                chapter_ref_id=UpdateAction.change_to(None),
                goal_ref_id=UpdateAction.do_nothing(),
            )
            await uow.get_for(HabitStack).save(updated_habit_stack)
            await progress_reporter.mark_updated(updated_habit_stack)

        # Unlink from TimePlans
        await uow.get(TimePlanChapterLinkRepository).remove_all_for_chapter(
            chapter.ref_id
        )
