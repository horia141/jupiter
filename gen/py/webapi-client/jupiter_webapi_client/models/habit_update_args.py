from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.habit_update_args_actionable_from_day import HabitUpdateArgsActionableFromDay
    from ..models.habit_update_args_actionable_from_month import HabitUpdateArgsActionableFromMonth
    from ..models.habit_update_args_aspect_ref_id import HabitUpdateArgsAspectRefId
    from ..models.habit_update_args_chapter_ref_id import HabitUpdateArgsChapterRefId
    from ..models.habit_update_args_difficulty import HabitUpdateArgsDifficulty
    from ..models.habit_update_args_due_at_day import HabitUpdateArgsDueAtDay
    from ..models.habit_update_args_due_at_month import HabitUpdateArgsDueAtMonth
    from ..models.habit_update_args_eisen import HabitUpdateArgsEisen
    from ..models.habit_update_args_goal_ref_id import HabitUpdateArgsGoalRefId
    from ..models.habit_update_args_is_key import HabitUpdateArgsIsKey
    from ..models.habit_update_args_name import HabitUpdateArgsName
    from ..models.habit_update_args_repeats_in_period_count import HabitUpdateArgsRepeatsInPeriodCount
    from ..models.habit_update_args_repeats_strategy import HabitUpdateArgsRepeatsStrategy
    from ..models.habit_update_args_schedulability import HabitUpdateArgsSchedulability
    from ..models.habit_update_args_scheduling_event_count import HabitUpdateArgsSchedulingEventCount
    from ..models.habit_update_args_scheduling_event_duration_mins import HabitUpdateArgsSchedulingEventDurationMins
    from ..models.habit_update_args_skip_rule import HabitUpdateArgsSkipRule
    from ..models.habit_update_args_stack_ref_id import HabitUpdateArgsStackRefId
    from ..models.habit_update_args_suspended import HabitUpdateArgsSuspended


T = TypeVar("T", bound="HabitUpdateArgs")


@_attrs_define
class HabitUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (HabitUpdateArgsName):
        aspect_ref_id (HabitUpdateArgsAspectRefId):
        chapter_ref_id (HabitUpdateArgsChapterRefId):
        goal_ref_id (HabitUpdateArgsGoalRefId):
        stack_ref_id (HabitUpdateArgsStackRefId):
        is_key (HabitUpdateArgsIsKey):
        eisen (HabitUpdateArgsEisen):
        difficulty (HabitUpdateArgsDifficulty):
        actionable_from_day (HabitUpdateArgsActionableFromDay):
        actionable_from_month (HabitUpdateArgsActionableFromMonth):
        due_at_day (HabitUpdateArgsDueAtDay):
        due_at_month (HabitUpdateArgsDueAtMonth):
        skip_rule (HabitUpdateArgsSkipRule):
        repeats_strategy (HabitUpdateArgsRepeatsStrategy):
        repeats_in_period_count (HabitUpdateArgsRepeatsInPeriodCount):
        schedulability (HabitUpdateArgsSchedulability):
        scheduling_event_duration_mins (HabitUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (HabitUpdateArgsSchedulingEventCount):
        suspended (HabitUpdateArgsSuspended):
    """

    ref_id: str
    name: HabitUpdateArgsName
    aspect_ref_id: HabitUpdateArgsAspectRefId
    chapter_ref_id: HabitUpdateArgsChapterRefId
    goal_ref_id: HabitUpdateArgsGoalRefId
    stack_ref_id: HabitUpdateArgsStackRefId
    is_key: HabitUpdateArgsIsKey
    eisen: HabitUpdateArgsEisen
    difficulty: HabitUpdateArgsDifficulty
    actionable_from_day: HabitUpdateArgsActionableFromDay
    actionable_from_month: HabitUpdateArgsActionableFromMonth
    due_at_day: HabitUpdateArgsDueAtDay
    due_at_month: HabitUpdateArgsDueAtMonth
    skip_rule: HabitUpdateArgsSkipRule
    repeats_strategy: HabitUpdateArgsRepeatsStrategy
    repeats_in_period_count: HabitUpdateArgsRepeatsInPeriodCount
    schedulability: HabitUpdateArgsSchedulability
    scheduling_event_duration_mins: HabitUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: HabitUpdateArgsSchedulingEventCount
    suspended: HabitUpdateArgsSuspended
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        aspect_ref_id = self.aspect_ref_id.to_dict()

        chapter_ref_id = self.chapter_ref_id.to_dict()

        goal_ref_id = self.goal_ref_id.to_dict()

        stack_ref_id = self.stack_ref_id.to_dict()

        is_key = self.is_key.to_dict()

        eisen = self.eisen.to_dict()

        difficulty = self.difficulty.to_dict()

        actionable_from_day = self.actionable_from_day.to_dict()

        actionable_from_month = self.actionable_from_month.to_dict()

        due_at_day = self.due_at_day.to_dict()

        due_at_month = self.due_at_month.to_dict()

        skip_rule = self.skip_rule.to_dict()

        repeats_strategy = self.repeats_strategy.to_dict()

        repeats_in_period_count = self.repeats_in_period_count.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        suspended = self.suspended.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "aspect_ref_id": aspect_ref_id,
                "chapter_ref_id": chapter_ref_id,
                "goal_ref_id": goal_ref_id,
                "stack_ref_id": stack_ref_id,
                "is_key": is_key,
                "eisen": eisen,
                "difficulty": difficulty,
                "actionable_from_day": actionable_from_day,
                "actionable_from_month": actionable_from_month,
                "due_at_day": due_at_day,
                "due_at_month": due_at_month,
                "skip_rule": skip_rule,
                "repeats_strategy": repeats_strategy,
                "repeats_in_period_count": repeats_in_period_count,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
                "suspended": suspended,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.habit_update_args_actionable_from_day import HabitUpdateArgsActionableFromDay  # noqa: PLC0415
        from ..models.habit_update_args_actionable_from_month import HabitUpdateArgsActionableFromMonth  # noqa: PLC0415
        from ..models.habit_update_args_aspect_ref_id import HabitUpdateArgsAspectRefId  # noqa: PLC0415
        from ..models.habit_update_args_chapter_ref_id import HabitUpdateArgsChapterRefId  # noqa: PLC0415
        from ..models.habit_update_args_difficulty import HabitUpdateArgsDifficulty  # noqa: PLC0415
        from ..models.habit_update_args_due_at_day import HabitUpdateArgsDueAtDay  # noqa: PLC0415
        from ..models.habit_update_args_due_at_month import HabitUpdateArgsDueAtMonth  # noqa: PLC0415
        from ..models.habit_update_args_eisen import HabitUpdateArgsEisen  # noqa: PLC0415
        from ..models.habit_update_args_goal_ref_id import HabitUpdateArgsGoalRefId  # noqa: PLC0415
        from ..models.habit_update_args_is_key import HabitUpdateArgsIsKey  # noqa: PLC0415
        from ..models.habit_update_args_name import HabitUpdateArgsName  # noqa: PLC0415
        from ..models.habit_update_args_repeats_in_period_count import HabitUpdateArgsRepeatsInPeriodCount  # noqa: PLC0415
        from ..models.habit_update_args_repeats_strategy import HabitUpdateArgsRepeatsStrategy  # noqa: PLC0415
        from ..models.habit_update_args_schedulability import HabitUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.habit_update_args_scheduling_event_count import HabitUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.habit_update_args_scheduling_event_duration_mins import HabitUpdateArgsSchedulingEventDurationMins  # noqa: PLC0415
        from ..models.habit_update_args_skip_rule import HabitUpdateArgsSkipRule  # noqa: PLC0415
        from ..models.habit_update_args_stack_ref_id import HabitUpdateArgsStackRefId  # noqa: PLC0415
        from ..models.habit_update_args_suspended import HabitUpdateArgsSuspended  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = HabitUpdateArgsName.from_dict(d.pop("name"))

        aspect_ref_id = HabitUpdateArgsAspectRefId.from_dict(d.pop("aspect_ref_id"))

        chapter_ref_id = HabitUpdateArgsChapterRefId.from_dict(d.pop("chapter_ref_id"))

        goal_ref_id = HabitUpdateArgsGoalRefId.from_dict(d.pop("goal_ref_id"))

        stack_ref_id = HabitUpdateArgsStackRefId.from_dict(d.pop("stack_ref_id"))

        is_key = HabitUpdateArgsIsKey.from_dict(d.pop("is_key"))

        eisen = HabitUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = HabitUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_from_day = HabitUpdateArgsActionableFromDay.from_dict(d.pop("actionable_from_day"))

        actionable_from_month = HabitUpdateArgsActionableFromMonth.from_dict(d.pop("actionable_from_month"))

        due_at_day = HabitUpdateArgsDueAtDay.from_dict(d.pop("due_at_day"))

        due_at_month = HabitUpdateArgsDueAtMonth.from_dict(d.pop("due_at_month"))

        skip_rule = HabitUpdateArgsSkipRule.from_dict(d.pop("skip_rule"))

        repeats_strategy = HabitUpdateArgsRepeatsStrategy.from_dict(d.pop("repeats_strategy"))

        repeats_in_period_count = HabitUpdateArgsRepeatsInPeriodCount.from_dict(d.pop("repeats_in_period_count"))

        schedulability = HabitUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = HabitUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = HabitUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        suspended = HabitUpdateArgsSuspended.from_dict(d.pop("suspended"))

        habit_update_args = cls(
            ref_id=ref_id,
            name=name,
            aspect_ref_id=aspect_ref_id,
            chapter_ref_id=chapter_ref_id,
            goal_ref_id=goal_ref_id,
            stack_ref_id=stack_ref_id,
            is_key=is_key,
            eisen=eisen,
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            repeats_strategy=repeats_strategy,
            repeats_in_period_count=repeats_in_period_count,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
            suspended=suspended,
        )

        habit_update_args.additional_properties = d
        return habit_update_args

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
