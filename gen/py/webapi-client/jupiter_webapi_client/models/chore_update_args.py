from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chore_update_args_actionable_from_day import ChoreUpdateArgsActionableFromDay
    from ..models.chore_update_args_actionable_from_month import ChoreUpdateArgsActionableFromMonth
    from ..models.chore_update_args_aspect_ref_id import ChoreUpdateArgsAspectRefId
    from ..models.chore_update_args_chapter_ref_id import ChoreUpdateArgsChapterRefId
    from ..models.chore_update_args_difficulty import ChoreUpdateArgsDifficulty
    from ..models.chore_update_args_due_at_day import ChoreUpdateArgsDueAtDay
    from ..models.chore_update_args_due_at_month import ChoreUpdateArgsDueAtMonth
    from ..models.chore_update_args_eisen import ChoreUpdateArgsEisen
    from ..models.chore_update_args_end_at_date import ChoreUpdateArgsEndAtDate
    from ..models.chore_update_args_goal_ref_id import ChoreUpdateArgsGoalRefId
    from ..models.chore_update_args_is_key import ChoreUpdateArgsIsKey
    from ..models.chore_update_args_must_do import ChoreUpdateArgsMustDo
    from ..models.chore_update_args_name import ChoreUpdateArgsName
    from ..models.chore_update_args_schedulability import ChoreUpdateArgsSchedulability
    from ..models.chore_update_args_scheduling_event_count import ChoreUpdateArgsSchedulingEventCount
    from ..models.chore_update_args_scheduling_event_duration_mins import ChoreUpdateArgsSchedulingEventDurationMins
    from ..models.chore_update_args_skip_rule import ChoreUpdateArgsSkipRule
    from ..models.chore_update_args_stack_ref_id import ChoreUpdateArgsStackRefId
    from ..models.chore_update_args_start_at_date import ChoreUpdateArgsStartAtDate
    from ..models.chore_update_args_suspended import ChoreUpdateArgsSuspended


T = TypeVar("T", bound="ChoreUpdateArgs")


@_attrs_define
class ChoreUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (ChoreUpdateArgsName):
        aspect_ref_id (ChoreUpdateArgsAspectRefId):
        chapter_ref_id (ChoreUpdateArgsChapterRefId):
        goal_ref_id (ChoreUpdateArgsGoalRefId):
        stack_ref_id (ChoreUpdateArgsStackRefId):
        is_key (ChoreUpdateArgsIsKey):
        eisen (ChoreUpdateArgsEisen):
        difficulty (ChoreUpdateArgsDifficulty):
        actionable_from_day (ChoreUpdateArgsActionableFromDay):
        actionable_from_month (ChoreUpdateArgsActionableFromMonth):
        due_at_day (ChoreUpdateArgsDueAtDay):
        due_at_month (ChoreUpdateArgsDueAtMonth):
        must_do (ChoreUpdateArgsMustDo):
        skip_rule (ChoreUpdateArgsSkipRule):
        start_at_date (ChoreUpdateArgsStartAtDate):
        end_at_date (ChoreUpdateArgsEndAtDate):
        schedulability (ChoreUpdateArgsSchedulability):
        scheduling_event_duration_mins (ChoreUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (ChoreUpdateArgsSchedulingEventCount):
        suspended (ChoreUpdateArgsSuspended):
    """

    ref_id: str
    name: ChoreUpdateArgsName
    aspect_ref_id: ChoreUpdateArgsAspectRefId
    chapter_ref_id: ChoreUpdateArgsChapterRefId
    goal_ref_id: ChoreUpdateArgsGoalRefId
    stack_ref_id: ChoreUpdateArgsStackRefId
    is_key: ChoreUpdateArgsIsKey
    eisen: ChoreUpdateArgsEisen
    difficulty: ChoreUpdateArgsDifficulty
    actionable_from_day: ChoreUpdateArgsActionableFromDay
    actionable_from_month: ChoreUpdateArgsActionableFromMonth
    due_at_day: ChoreUpdateArgsDueAtDay
    due_at_month: ChoreUpdateArgsDueAtMonth
    must_do: ChoreUpdateArgsMustDo
    skip_rule: ChoreUpdateArgsSkipRule
    start_at_date: ChoreUpdateArgsStartAtDate
    end_at_date: ChoreUpdateArgsEndAtDate
    schedulability: ChoreUpdateArgsSchedulability
    scheduling_event_duration_mins: ChoreUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: ChoreUpdateArgsSchedulingEventCount
    suspended: ChoreUpdateArgsSuspended
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

        must_do = self.must_do.to_dict()

        skip_rule = self.skip_rule.to_dict()

        start_at_date = self.start_at_date.to_dict()

        end_at_date = self.end_at_date.to_dict()

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
                "must_do": must_do,
                "skip_rule": skip_rule,
                "start_at_date": start_at_date,
                "end_at_date": end_at_date,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
                "suspended": suspended,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chore_update_args_actionable_from_day import ChoreUpdateArgsActionableFromDay  # noqa: PLC0415
        from ..models.chore_update_args_actionable_from_month import ChoreUpdateArgsActionableFromMonth  # noqa: PLC0415
        from ..models.chore_update_args_aspect_ref_id import ChoreUpdateArgsAspectRefId  # noqa: PLC0415
        from ..models.chore_update_args_chapter_ref_id import ChoreUpdateArgsChapterRefId  # noqa: PLC0415
        from ..models.chore_update_args_difficulty import ChoreUpdateArgsDifficulty  # noqa: PLC0415
        from ..models.chore_update_args_due_at_day import ChoreUpdateArgsDueAtDay  # noqa: PLC0415
        from ..models.chore_update_args_due_at_month import ChoreUpdateArgsDueAtMonth  # noqa: PLC0415
        from ..models.chore_update_args_eisen import ChoreUpdateArgsEisen  # noqa: PLC0415
        from ..models.chore_update_args_end_at_date import ChoreUpdateArgsEndAtDate  # noqa: PLC0415
        from ..models.chore_update_args_goal_ref_id import ChoreUpdateArgsGoalRefId  # noqa: PLC0415
        from ..models.chore_update_args_is_key import ChoreUpdateArgsIsKey  # noqa: PLC0415
        from ..models.chore_update_args_must_do import ChoreUpdateArgsMustDo  # noqa: PLC0415
        from ..models.chore_update_args_name import ChoreUpdateArgsName  # noqa: PLC0415
        from ..models.chore_update_args_schedulability import ChoreUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.chore_update_args_scheduling_event_count import ChoreUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.chore_update_args_scheduling_event_duration_mins import ChoreUpdateArgsSchedulingEventDurationMins  # noqa: PLC0415
        from ..models.chore_update_args_skip_rule import ChoreUpdateArgsSkipRule  # noqa: PLC0415
        from ..models.chore_update_args_stack_ref_id import ChoreUpdateArgsStackRefId  # noqa: PLC0415
        from ..models.chore_update_args_start_at_date import ChoreUpdateArgsStartAtDate  # noqa: PLC0415
        from ..models.chore_update_args_suspended import ChoreUpdateArgsSuspended  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = ChoreUpdateArgsName.from_dict(d.pop("name"))

        aspect_ref_id = ChoreUpdateArgsAspectRefId.from_dict(d.pop("aspect_ref_id"))

        chapter_ref_id = ChoreUpdateArgsChapterRefId.from_dict(d.pop("chapter_ref_id"))

        goal_ref_id = ChoreUpdateArgsGoalRefId.from_dict(d.pop("goal_ref_id"))

        stack_ref_id = ChoreUpdateArgsStackRefId.from_dict(d.pop("stack_ref_id"))

        is_key = ChoreUpdateArgsIsKey.from_dict(d.pop("is_key"))

        eisen = ChoreUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = ChoreUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_from_day = ChoreUpdateArgsActionableFromDay.from_dict(d.pop("actionable_from_day"))

        actionable_from_month = ChoreUpdateArgsActionableFromMonth.from_dict(d.pop("actionable_from_month"))

        due_at_day = ChoreUpdateArgsDueAtDay.from_dict(d.pop("due_at_day"))

        due_at_month = ChoreUpdateArgsDueAtMonth.from_dict(d.pop("due_at_month"))

        must_do = ChoreUpdateArgsMustDo.from_dict(d.pop("must_do"))

        skip_rule = ChoreUpdateArgsSkipRule.from_dict(d.pop("skip_rule"))

        start_at_date = ChoreUpdateArgsStartAtDate.from_dict(d.pop("start_at_date"))

        end_at_date = ChoreUpdateArgsEndAtDate.from_dict(d.pop("end_at_date"))

        schedulability = ChoreUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = ChoreUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = ChoreUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        suspended = ChoreUpdateArgsSuspended.from_dict(d.pop("suspended"))

        chore_update_args = cls(
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
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date,
            end_at_date=end_at_date,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
            suspended=suspended,
        )

        chore_update_args.additional_properties = d
        return chore_update_args

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
