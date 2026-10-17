from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_status import AccessStatus
    from ..models.aspect import Aspect
    from ..models.big_plan import BigPlan
    from ..models.big_plan_stats import BigPlanStats
    from ..models.chapter import Chapter
    from ..models.chore import Chore
    from ..models.chore_stack import ChoreStack
    from ..models.goal import Goal
    from ..models.habit import Habit
    from ..models.habit_stack import HabitStack
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.publish_entity import PublishEntity
    from ..models.tag import Tag
    from ..models.time_event_in_day_block import TimeEventInDayBlock
    from ..models.time_plan import TimePlan
    from ..models.time_plan_activity import TimePlanActivity
    from ..models.time_plan_load_result_activity_doneness_type_0 import TimePlanLoadResultActivityDonenessType0
    from ..models.todo_task import TodoTask
    from ..models.user_light import UserLight


T = TypeVar("T", bound="TimePlanLoadResult")


@_attrs_define
class TimePlanLoadResult:
    """TimePlanLoadResult.

    Attributes:
        time_plan (TimePlan): A plan for a particular period of time.
        tags (list[Tag]):
        note (Note): A note in the notebook.
        activities (list[TimePlanActivity]):
        activity_time_event_blocks (list[TimeEventInDayBlock]):
        chapters (list[Chapter]):
        aspects (list[Aspect]):
        goals (list[Goal]):
        owner (UserLight): A user's ref id, name, and email address.
        target_inbox_tasks (list[InboxTask] | None | Unset):
        target_big_plans (list[BigPlan] | None | Unset):
        big_plan_stats (list[BigPlanStats] | None | Unset):
        target_todo_tasks (list[TodoTask] | None | Unset):
        target_habits (list[Habit] | None | Unset):
        target_habit_stacks (list[HabitStack] | None | Unset):
        target_chores (list[Chore] | None | Unset):
        target_chore_stacks (list[ChoreStack] | None | Unset):
        activity_doneness (None | TimePlanLoadResultActivityDonenessType0 | Unset):
        completed_nontarget_inbox_tasks (list[InboxTask] | None | Unset):
        completed_nottarget_big_plans (list[BigPlan] | None | Unset):
        sub_period_time_plans (list[TimePlan] | None | Unset):
        higher_time_plan (None | TimePlan | Unset):
        previous_time_plan (None | TimePlan | Unset):
        publish_entity (None | PublishEntity | Unset):
        access_status (AccessStatus | None | Unset):
    """

    time_plan: TimePlan
    tags: list[Tag]
    note: Note
    activities: list[TimePlanActivity]
    activity_time_event_blocks: list[TimeEventInDayBlock]
    chapters: list[Chapter]
    aspects: list[Aspect]
    goals: list[Goal]
    owner: UserLight
    target_inbox_tasks: list[InboxTask] | None | Unset = UNSET
    target_big_plans: list[BigPlan] | None | Unset = UNSET
    big_plan_stats: list[BigPlanStats] | None | Unset = UNSET
    target_todo_tasks: list[TodoTask] | None | Unset = UNSET
    target_habits: list[Habit] | None | Unset = UNSET
    target_habit_stacks: list[HabitStack] | None | Unset = UNSET
    target_chores: list[Chore] | None | Unset = UNSET
    target_chore_stacks: list[ChoreStack] | None | Unset = UNSET
    activity_doneness: None | TimePlanLoadResultActivityDonenessType0 | Unset = UNSET
    completed_nontarget_inbox_tasks: list[InboxTask] | None | Unset = UNSET
    completed_nottarget_big_plans: list[BigPlan] | None | Unset = UNSET
    sub_period_time_plans: list[TimePlan] | None | Unset = UNSET
    higher_time_plan: None | TimePlan | Unset = UNSET
    previous_time_plan: None | TimePlan | Unset = UNSET
    publish_entity: None | PublishEntity | Unset = UNSET
    access_status: AccessStatus | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415
        from ..models.time_plan import TimePlan  # noqa: PLC0415
        from ..models.time_plan_load_result_activity_doneness_type_0 import TimePlanLoadResultActivityDonenessType0  # noqa: PLC0415

        time_plan = self.time_plan.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        note = self.note.to_dict()

        activities = []
        for activities_item_data in self.activities:
            activities_item = activities_item_data.to_dict()
            activities.append(activities_item)

        activity_time_event_blocks = []
        for activity_time_event_blocks_item_data in self.activity_time_event_blocks:
            activity_time_event_blocks_item = activity_time_event_blocks_item_data.to_dict()
            activity_time_event_blocks.append(activity_time_event_blocks_item)

        chapters = []
        for chapters_item_data in self.chapters:
            chapters_item = chapters_item_data.to_dict()
            chapters.append(chapters_item)

        aspects = []
        for aspects_item_data in self.aspects:
            aspects_item = aspects_item_data.to_dict()
            aspects.append(aspects_item)

        goals = []
        for goals_item_data in self.goals:
            goals_item = goals_item_data.to_dict()
            goals.append(goals_item)

        owner = self.owner.to_dict()

        target_inbox_tasks: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_inbox_tasks, Unset):
            target_inbox_tasks = UNSET
        elif isinstance(self.target_inbox_tasks, list):
            target_inbox_tasks = []
            for target_inbox_tasks_type_0_item_data in self.target_inbox_tasks:
                target_inbox_tasks_type_0_item = target_inbox_tasks_type_0_item_data.to_dict()
                target_inbox_tasks.append(target_inbox_tasks_type_0_item)

        else:
            target_inbox_tasks = self.target_inbox_tasks

        target_big_plans: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_big_plans, Unset):
            target_big_plans = UNSET
        elif isinstance(self.target_big_plans, list):
            target_big_plans = []
            for target_big_plans_type_0_item_data in self.target_big_plans:
                target_big_plans_type_0_item = target_big_plans_type_0_item_data.to_dict()
                target_big_plans.append(target_big_plans_type_0_item)

        else:
            target_big_plans = self.target_big_plans

        big_plan_stats: list[dict[str, Any]] | None | Unset
        if isinstance(self.big_plan_stats, Unset):
            big_plan_stats = UNSET
        elif isinstance(self.big_plan_stats, list):
            big_plan_stats = []
            for big_plan_stats_type_0_item_data in self.big_plan_stats:
                big_plan_stats_type_0_item = big_plan_stats_type_0_item_data.to_dict()
                big_plan_stats.append(big_plan_stats_type_0_item)

        else:
            big_plan_stats = self.big_plan_stats

        target_todo_tasks: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_todo_tasks, Unset):
            target_todo_tasks = UNSET
        elif isinstance(self.target_todo_tasks, list):
            target_todo_tasks = []
            for target_todo_tasks_type_0_item_data in self.target_todo_tasks:
                target_todo_tasks_type_0_item = target_todo_tasks_type_0_item_data.to_dict()
                target_todo_tasks.append(target_todo_tasks_type_0_item)

        else:
            target_todo_tasks = self.target_todo_tasks

        target_habits: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_habits, Unset):
            target_habits = UNSET
        elif isinstance(self.target_habits, list):
            target_habits = []
            for target_habits_type_0_item_data in self.target_habits:
                target_habits_type_0_item = target_habits_type_0_item_data.to_dict()
                target_habits.append(target_habits_type_0_item)

        else:
            target_habits = self.target_habits

        target_habit_stacks: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_habit_stacks, Unset):
            target_habit_stacks = UNSET
        elif isinstance(self.target_habit_stacks, list):
            target_habit_stacks = []
            for target_habit_stacks_type_0_item_data in self.target_habit_stacks:
                target_habit_stacks_type_0_item = target_habit_stacks_type_0_item_data.to_dict()
                target_habit_stacks.append(target_habit_stacks_type_0_item)

        else:
            target_habit_stacks = self.target_habit_stacks

        target_chores: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_chores, Unset):
            target_chores = UNSET
        elif isinstance(self.target_chores, list):
            target_chores = []
            for target_chores_type_0_item_data in self.target_chores:
                target_chores_type_0_item = target_chores_type_0_item_data.to_dict()
                target_chores.append(target_chores_type_0_item)

        else:
            target_chores = self.target_chores

        target_chore_stacks: list[dict[str, Any]] | None | Unset
        if isinstance(self.target_chore_stacks, Unset):
            target_chore_stacks = UNSET
        elif isinstance(self.target_chore_stacks, list):
            target_chore_stacks = []
            for target_chore_stacks_type_0_item_data in self.target_chore_stacks:
                target_chore_stacks_type_0_item = target_chore_stacks_type_0_item_data.to_dict()
                target_chore_stacks.append(target_chore_stacks_type_0_item)

        else:
            target_chore_stacks = self.target_chore_stacks

        activity_doneness: dict[str, Any] | None | Unset
        if isinstance(self.activity_doneness, Unset):
            activity_doneness = UNSET
        elif isinstance(self.activity_doneness, TimePlanLoadResultActivityDonenessType0):
            activity_doneness = self.activity_doneness.to_dict()
        else:
            activity_doneness = self.activity_doneness

        completed_nontarget_inbox_tasks: list[dict[str, Any]] | None | Unset
        if isinstance(self.completed_nontarget_inbox_tasks, Unset):
            completed_nontarget_inbox_tasks = UNSET
        elif isinstance(self.completed_nontarget_inbox_tasks, list):
            completed_nontarget_inbox_tasks = []
            for completed_nontarget_inbox_tasks_type_0_item_data in self.completed_nontarget_inbox_tasks:
                completed_nontarget_inbox_tasks_type_0_item = completed_nontarget_inbox_tasks_type_0_item_data.to_dict()
                completed_nontarget_inbox_tasks.append(completed_nontarget_inbox_tasks_type_0_item)

        else:
            completed_nontarget_inbox_tasks = self.completed_nontarget_inbox_tasks

        completed_nottarget_big_plans: list[dict[str, Any]] | None | Unset
        if isinstance(self.completed_nottarget_big_plans, Unset):
            completed_nottarget_big_plans = UNSET
        elif isinstance(self.completed_nottarget_big_plans, list):
            completed_nottarget_big_plans = []
            for completed_nottarget_big_plans_type_0_item_data in self.completed_nottarget_big_plans:
                completed_nottarget_big_plans_type_0_item = completed_nottarget_big_plans_type_0_item_data.to_dict()
                completed_nottarget_big_plans.append(completed_nottarget_big_plans_type_0_item)

        else:
            completed_nottarget_big_plans = self.completed_nottarget_big_plans

        sub_period_time_plans: list[dict[str, Any]] | None | Unset
        if isinstance(self.sub_period_time_plans, Unset):
            sub_period_time_plans = UNSET
        elif isinstance(self.sub_period_time_plans, list):
            sub_period_time_plans = []
            for sub_period_time_plans_type_0_item_data in self.sub_period_time_plans:
                sub_period_time_plans_type_0_item = sub_period_time_plans_type_0_item_data.to_dict()
                sub_period_time_plans.append(sub_period_time_plans_type_0_item)

        else:
            sub_period_time_plans = self.sub_period_time_plans

        higher_time_plan: dict[str, Any] | None | Unset
        if isinstance(self.higher_time_plan, Unset):
            higher_time_plan = UNSET
        elif isinstance(self.higher_time_plan, TimePlan):
            higher_time_plan = self.higher_time_plan.to_dict()
        else:
            higher_time_plan = self.higher_time_plan

        previous_time_plan: dict[str, Any] | None | Unset
        if isinstance(self.previous_time_plan, Unset):
            previous_time_plan = UNSET
        elif isinstance(self.previous_time_plan, TimePlan):
            previous_time_plan = self.previous_time_plan.to_dict()
        else:
            previous_time_plan = self.previous_time_plan

        publish_entity: dict[str, Any] | None | Unset
        if isinstance(self.publish_entity, Unset):
            publish_entity = UNSET
        elif isinstance(self.publish_entity, PublishEntity):
            publish_entity = self.publish_entity.to_dict()
        else:
            publish_entity = self.publish_entity

        access_status: dict[str, Any] | None | Unset
        if isinstance(self.access_status, Unset):
            access_status = UNSET
        elif isinstance(self.access_status, AccessStatus):
            access_status = self.access_status.to_dict()
        else:
            access_status = self.access_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan": time_plan,
                "tags": tags,
                "note": note,
                "activities": activities,
                "activity_time_event_blocks": activity_time_event_blocks,
                "chapters": chapters,
                "aspects": aspects,
                "goals": goals,
                "owner": owner,
            }
        )
        if target_inbox_tasks is not UNSET:
            field_dict["target_inbox_tasks"] = target_inbox_tasks
        if target_big_plans is not UNSET:
            field_dict["target_big_plans"] = target_big_plans
        if big_plan_stats is not UNSET:
            field_dict["big_plan_stats"] = big_plan_stats
        if target_todo_tasks is not UNSET:
            field_dict["target_todo_tasks"] = target_todo_tasks
        if target_habits is not UNSET:
            field_dict["target_habits"] = target_habits
        if target_habit_stacks is not UNSET:
            field_dict["target_habit_stacks"] = target_habit_stacks
        if target_chores is not UNSET:
            field_dict["target_chores"] = target_chores
        if target_chore_stacks is not UNSET:
            field_dict["target_chore_stacks"] = target_chore_stacks
        if activity_doneness is not UNSET:
            field_dict["activity_doneness"] = activity_doneness
        if completed_nontarget_inbox_tasks is not UNSET:
            field_dict["completed_nontarget_inbox_tasks"] = completed_nontarget_inbox_tasks
        if completed_nottarget_big_plans is not UNSET:
            field_dict["completed_nottarget_big_plans"] = completed_nottarget_big_plans
        if sub_period_time_plans is not UNSET:
            field_dict["sub_period_time_plans"] = sub_period_time_plans
        if higher_time_plan is not UNSET:
            field_dict["higher_time_plan"] = higher_time_plan
        if previous_time_plan is not UNSET:
            field_dict["previous_time_plan"] = previous_time_plan
        if publish_entity is not UNSET:
            field_dict["publish_entity"] = publish_entity
        if access_status is not UNSET:
            field_dict["access_status"] = access_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.aspect import Aspect  # noqa: PLC0415
        from ..models.big_plan import BigPlan  # noqa: PLC0415
        from ..models.big_plan_stats import BigPlanStats  # noqa: PLC0415
        from ..models.chapter import Chapter  # noqa: PLC0415
        from ..models.chore import Chore  # noqa: PLC0415
        from ..models.chore_stack import ChoreStack  # noqa: PLC0415
        from ..models.goal import Goal  # noqa: PLC0415
        from ..models.habit import Habit  # noqa: PLC0415
        from ..models.habit_stack import HabitStack  # noqa: PLC0415
        from ..models.inbox_task import InboxTask  # noqa: PLC0415
        from ..models.note import Note  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415
        from ..models.tag import Tag  # noqa: PLC0415
        from ..models.time_event_in_day_block import TimeEventInDayBlock  # noqa: PLC0415
        from ..models.time_plan import TimePlan  # noqa: PLC0415
        from ..models.time_plan_activity import TimePlanActivity  # noqa: PLC0415
        from ..models.time_plan_load_result_activity_doneness_type_0 import TimePlanLoadResultActivityDonenessType0  # noqa: PLC0415
        from ..models.todo_task import TodoTask  # noqa: PLC0415
        from ..models.user_light import UserLight  # noqa: PLC0415

        d = dict(src_dict)
        time_plan = TimePlan.from_dict(d.pop("time_plan"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        note = Note.from_dict(d.pop("note"))

        activities = []
        _activities = d.pop("activities")
        for activities_item_data in _activities:
            activities_item = TimePlanActivity.from_dict(activities_item_data)

            activities.append(activities_item)

        activity_time_event_blocks = []
        _activity_time_event_blocks = d.pop("activity_time_event_blocks")
        for activity_time_event_blocks_item_data in _activity_time_event_blocks:
            activity_time_event_blocks_item = TimeEventInDayBlock.from_dict(activity_time_event_blocks_item_data)

            activity_time_event_blocks.append(activity_time_event_blocks_item)

        chapters = []
        _chapters = d.pop("chapters")
        for chapters_item_data in _chapters:
            chapters_item = Chapter.from_dict(chapters_item_data)

            chapters.append(chapters_item)

        aspects = []
        _aspects = d.pop("aspects")
        for aspects_item_data in _aspects:
            aspects_item = Aspect.from_dict(aspects_item_data)

            aspects.append(aspects_item)

        goals = []
        _goals = d.pop("goals")
        for goals_item_data in _goals:
            goals_item = Goal.from_dict(goals_item_data)

            goals.append(goals_item)

        owner = UserLight.from_dict(d.pop("owner"))

        def _parse_target_inbox_tasks(data: object) -> list[InboxTask] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_inbox_tasks_type_0 = []
                _target_inbox_tasks_type_0 = data
                for target_inbox_tasks_type_0_item_data in _target_inbox_tasks_type_0:
                    target_inbox_tasks_type_0_item = InboxTask.from_dict(target_inbox_tasks_type_0_item_data)

                    target_inbox_tasks_type_0.append(target_inbox_tasks_type_0_item)

                return target_inbox_tasks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[InboxTask] | None | Unset, data)

        target_inbox_tasks = _parse_target_inbox_tasks(d.pop("target_inbox_tasks", UNSET))

        def _parse_target_big_plans(data: object) -> list[BigPlan] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_big_plans_type_0 = []
                _target_big_plans_type_0 = data
                for target_big_plans_type_0_item_data in _target_big_plans_type_0:
                    target_big_plans_type_0_item = BigPlan.from_dict(target_big_plans_type_0_item_data)

                    target_big_plans_type_0.append(target_big_plans_type_0_item)

                return target_big_plans_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[BigPlan] | None | Unset, data)

        target_big_plans = _parse_target_big_plans(d.pop("target_big_plans", UNSET))

        def _parse_big_plan_stats(data: object) -> list[BigPlanStats] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                big_plan_stats_type_0 = []
                _big_plan_stats_type_0 = data
                for big_plan_stats_type_0_item_data in _big_plan_stats_type_0:
                    big_plan_stats_type_0_item = BigPlanStats.from_dict(big_plan_stats_type_0_item_data)

                    big_plan_stats_type_0.append(big_plan_stats_type_0_item)

                return big_plan_stats_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[BigPlanStats] | None | Unset, data)

        big_plan_stats = _parse_big_plan_stats(d.pop("big_plan_stats", UNSET))

        def _parse_target_todo_tasks(data: object) -> list[TodoTask] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_todo_tasks_type_0 = []
                _target_todo_tasks_type_0 = data
                for target_todo_tasks_type_0_item_data in _target_todo_tasks_type_0:
                    target_todo_tasks_type_0_item = TodoTask.from_dict(target_todo_tasks_type_0_item_data)

                    target_todo_tasks_type_0.append(target_todo_tasks_type_0_item)

                return target_todo_tasks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[TodoTask] | None | Unset, data)

        target_todo_tasks = _parse_target_todo_tasks(d.pop("target_todo_tasks", UNSET))

        def _parse_target_habits(data: object) -> list[Habit] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_habits_type_0 = []
                _target_habits_type_0 = data
                for target_habits_type_0_item_data in _target_habits_type_0:
                    target_habits_type_0_item = Habit.from_dict(target_habits_type_0_item_data)

                    target_habits_type_0.append(target_habits_type_0_item)

                return target_habits_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Habit] | None | Unset, data)

        target_habits = _parse_target_habits(d.pop("target_habits", UNSET))

        def _parse_target_habit_stacks(data: object) -> list[HabitStack] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_habit_stacks_type_0 = []
                _target_habit_stacks_type_0 = data
                for target_habit_stacks_type_0_item_data in _target_habit_stacks_type_0:
                    target_habit_stacks_type_0_item = HabitStack.from_dict(target_habit_stacks_type_0_item_data)

                    target_habit_stacks_type_0.append(target_habit_stacks_type_0_item)

                return target_habit_stacks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[HabitStack] | None | Unset, data)

        target_habit_stacks = _parse_target_habit_stacks(d.pop("target_habit_stacks", UNSET))

        def _parse_target_chores(data: object) -> list[Chore] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_chores_type_0 = []
                _target_chores_type_0 = data
                for target_chores_type_0_item_data in _target_chores_type_0:
                    target_chores_type_0_item = Chore.from_dict(target_chores_type_0_item_data)

                    target_chores_type_0.append(target_chores_type_0_item)

                return target_chores_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Chore] | None | Unset, data)

        target_chores = _parse_target_chores(d.pop("target_chores", UNSET))

        def _parse_target_chore_stacks(data: object) -> list[ChoreStack] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_chore_stacks_type_0 = []
                _target_chore_stacks_type_0 = data
                for target_chore_stacks_type_0_item_data in _target_chore_stacks_type_0:
                    target_chore_stacks_type_0_item = ChoreStack.from_dict(target_chore_stacks_type_0_item_data)

                    target_chore_stacks_type_0.append(target_chore_stacks_type_0_item)

                return target_chore_stacks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ChoreStack] | None | Unset, data)

        target_chore_stacks = _parse_target_chore_stacks(d.pop("target_chore_stacks", UNSET))

        def _parse_activity_doneness(data: object) -> None | TimePlanLoadResultActivityDonenessType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                activity_doneness_type_0 = TimePlanLoadResultActivityDonenessType0.from_dict(data)

                return activity_doneness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TimePlanLoadResultActivityDonenessType0 | Unset, data)

        activity_doneness = _parse_activity_doneness(d.pop("activity_doneness", UNSET))

        def _parse_completed_nontarget_inbox_tasks(data: object) -> list[InboxTask] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                completed_nontarget_inbox_tasks_type_0 = []
                _completed_nontarget_inbox_tasks_type_0 = data
                for completed_nontarget_inbox_tasks_type_0_item_data in _completed_nontarget_inbox_tasks_type_0:
                    completed_nontarget_inbox_tasks_type_0_item = InboxTask.from_dict(
                        completed_nontarget_inbox_tasks_type_0_item_data
                    )

                    completed_nontarget_inbox_tasks_type_0.append(completed_nontarget_inbox_tasks_type_0_item)

                return completed_nontarget_inbox_tasks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[InboxTask] | None | Unset, data)

        completed_nontarget_inbox_tasks = _parse_completed_nontarget_inbox_tasks(
            d.pop("completed_nontarget_inbox_tasks", UNSET)
        )

        def _parse_completed_nottarget_big_plans(data: object) -> list[BigPlan] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                completed_nottarget_big_plans_type_0 = []
                _completed_nottarget_big_plans_type_0 = data
                for completed_nottarget_big_plans_type_0_item_data in _completed_nottarget_big_plans_type_0:
                    completed_nottarget_big_plans_type_0_item = BigPlan.from_dict(
                        completed_nottarget_big_plans_type_0_item_data
                    )

                    completed_nottarget_big_plans_type_0.append(completed_nottarget_big_plans_type_0_item)

                return completed_nottarget_big_plans_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[BigPlan] | None | Unset, data)

        completed_nottarget_big_plans = _parse_completed_nottarget_big_plans(
            d.pop("completed_nottarget_big_plans", UNSET)
        )

        def _parse_sub_period_time_plans(data: object) -> list[TimePlan] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sub_period_time_plans_type_0 = []
                _sub_period_time_plans_type_0 = data
                for sub_period_time_plans_type_0_item_data in _sub_period_time_plans_type_0:
                    sub_period_time_plans_type_0_item = TimePlan.from_dict(sub_period_time_plans_type_0_item_data)

                    sub_period_time_plans_type_0.append(sub_period_time_plans_type_0_item)

                return sub_period_time_plans_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[TimePlan] | None | Unset, data)

        sub_period_time_plans = _parse_sub_period_time_plans(d.pop("sub_period_time_plans", UNSET))

        def _parse_higher_time_plan(data: object) -> None | TimePlan | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                higher_time_plan_type_0 = TimePlan.from_dict(data)

                return higher_time_plan_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TimePlan | Unset, data)

        higher_time_plan = _parse_higher_time_plan(d.pop("higher_time_plan", UNSET))

        def _parse_previous_time_plan(data: object) -> None | TimePlan | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                previous_time_plan_type_0 = TimePlan.from_dict(data)

                return previous_time_plan_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TimePlan | Unset, data)

        previous_time_plan = _parse_previous_time_plan(d.pop("previous_time_plan", UNSET))

        def _parse_publish_entity(data: object) -> None | PublishEntity | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                publish_entity_type_0 = PublishEntity.from_dict(data)

                return publish_entity_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PublishEntity | Unset, data)

        publish_entity = _parse_publish_entity(d.pop("publish_entity", UNSET))

        def _parse_access_status(data: object) -> AccessStatus | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                access_status_type_0 = AccessStatus.from_dict(data)

                return access_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessStatus | None | Unset, data)

        access_status = _parse_access_status(d.pop("access_status", UNSET))

        time_plan_load_result = cls(
            time_plan=time_plan,
            tags=tags,
            note=note,
            activities=activities,
            activity_time_event_blocks=activity_time_event_blocks,
            chapters=chapters,
            aspects=aspects,
            goals=goals,
            owner=owner,
            target_inbox_tasks=target_inbox_tasks,
            target_big_plans=target_big_plans,
            big_plan_stats=big_plan_stats,
            target_todo_tasks=target_todo_tasks,
            target_habits=target_habits,
            target_habit_stacks=target_habit_stacks,
            target_chores=target_chores,
            target_chore_stacks=target_chore_stacks,
            activity_doneness=activity_doneness,
            completed_nontarget_inbox_tasks=completed_nontarget_inbox_tasks,
            completed_nottarget_big_plans=completed_nottarget_big_plans,
            sub_period_time_plans=sub_period_time_plans,
            higher_time_plan=higher_time_plan,
            previous_time_plan=previous_time_plan,
            publish_entity=publish_entity,
            access_status=access_status,
        )

        time_plan_load_result.additional_properties = d
        return time_plan_load_result

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
