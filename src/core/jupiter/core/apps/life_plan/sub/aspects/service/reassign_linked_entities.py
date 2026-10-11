"""Service for reassigning linked entities."""

from jupiter.core.apps.big_plans.collection import BigPlanCollection
from jupiter.core.apps.big_plans.root import BigPlan
from jupiter.core.apps.chores.collection import ChoreCollection
from jupiter.core.apps.chores.root import Chore
from jupiter.core.apps.chores.sub.stack.root import ChoreStack
from jupiter.core.apps.habits.collection import HabitCollection
from jupiter.core.apps.habits.sub.habit.root import Habit
from jupiter.core.apps.habits.sub.stack.root import HabitStack
from jupiter.core.apps.life_plan.root import LifePlan
from jupiter.core.apps.life_plan.sub.aspects.root import Aspect
from jupiter.core.apps.life_plan.sub.chapters.root import Chapter
from jupiter.core.apps.life_plan.sub.milestones.root import Milestone
from jupiter.core.apps.time_plans.life_plan_links import (
    TimePlanAspectLinkRepository,
)
from jupiter.core.workspaces.root import Workspace
from jupiter.framework.context import DomainContext
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.update_action import UpdateAction


class AspectReassignLinkedEntitiesService:
    """Service for reassigning linked entities."""

    async def reassign_linked_entities(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        old_aspect: Aspect,
        new_aspect: Aspect,
    ) -> None:
        """Reassign linked entities."""
        life_plan = await uow.get_for(LifePlan).load_by_parent(workspace.ref_id)

        await uow.get(TimePlanAspectLinkRepository).remove_all_for_aspect(
            old_aspect.ref_id
        )

        # Unlink from BigPlans
        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id
        )
        big_plans = await uow.get_for(BigPlan).find_all_generic(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            aspect_ref_id=old_aspect.ref_id,
        )

        big_plans_by_ref_id = {big_plan.ref_id: big_plan for big_plan in big_plans}
        for big_plan in big_plans:
            updated_big_plan = big_plan.update(
                ctx,
                name=UpdateAction.do_nothing(),
                status=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                chapter_ref_id=UpdateAction.do_nothing(),
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
            big_plans_by_ref_id[big_plan.ref_id] = updated_big_plan

        # Unlink from Chores
        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
            workspace.ref_id
        )
        chores = await uow.get_for(Chore).find_all_generic(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            aspect_ref_id=old_aspect.ref_id,
        )
        chores_by_ref_id = {chore.ref_id: chore for chore in chores}
        for chore in chores:
            updated_chore = chore.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                chapter_ref_id=UpdateAction.do_nothing(),
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
            chores_by_ref_id[chore.ref_id] = updated_chore

        chore_stacks = await uow.get_for(ChoreStack).find_all_generic(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            aspect_ref_id=old_aspect.ref_id,
        )
        for stack in chore_stacks:
            updated_stack = stack.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                chapter_ref_id=UpdateAction.do_nothing(),
                goal_ref_id=UpdateAction.do_nothing(),
            )
            await uow.get_for(ChoreStack).save(updated_stack)
            await progress_reporter.mark_updated(updated_stack)

        # Unlink from Habits
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id
        )
        habits = await uow.get_for(Habit).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            aspect_ref_id=old_aspect.ref_id,
        )
        habits_by_ref_id = {habit.ref_id: habit for habit in habits}
        for habit in habits:
            updated_habit = habit.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                chapter_ref_id=UpdateAction.do_nothing(),
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
            habits_by_ref_id[habit.ref_id] = updated_habit

        habit_stacks = await uow.get_for(HabitStack).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            aspect_ref_id=old_aspect.ref_id,
        )
        for habit_stack in habit_stacks:
            updated_habit_stack = habit_stack.update(
                ctx,
                name=UpdateAction.do_nothing(),
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                chapter_ref_id=UpdateAction.do_nothing(),
                goal_ref_id=UpdateAction.do_nothing(),
            )
            await uow.get_for(HabitStack).save(updated_habit_stack)
            await progress_reporter.mark_updated(updated_habit_stack)

        milestones = await uow.get_for(
            Milestone
        ).find_all_generic(  # pyright: ignore[reportUndefinedVariable]
            aspect_ref_id=old_aspect.ref_id,
        )
        for milestone in milestones:
            milestone = milestone.update(
                ctx,
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                name=UpdateAction.do_nothing(),
                date=UpdateAction.do_nothing(),
            )
            await uow.get_for(Milestone).save(milestone)
            await progress_reporter.mark_updated(milestone)

        chapters = await uow.get_for(
            Chapter
        ).find_all_generic(  # pyright: ignore[reportUndefinedVariable]
            aspect_ref_id=old_aspect.ref_id,
        )
        milestone_dates_by_ref_id = {
            milestone.ref_id: milestone.date for milestone in milestones
        }
        for chapter in chapters:
            chapter = chapter.update(
                ctx,
                birthday=life_plan.birthday_date,
                milestone_dates_by_ref_id=milestone_dates_by_ref_id,
                aspect_ref_id=UpdateAction.change_to(new_aspect.ref_id),
                name=UpdateAction.do_nothing(),
                start_date=UpdateAction.do_nothing(),
                end_date=UpdateAction.do_nothing(),
            )
            await uow.get_for(Chapter).save(chapter)
            await progress_reporter.mark_updated(chapter)
