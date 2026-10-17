from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.big_plan_update_args_actionable_date import BigPlanUpdateArgsActionableDate
    from ..models.big_plan_update_args_aspect_ref_id import BigPlanUpdateArgsAspectRefId
    from ..models.big_plan_update_args_chapter_ref_id import BigPlanUpdateArgsChapterRefId
    from ..models.big_plan_update_args_dependency_ref_ids import BigPlanUpdateArgsDependencyRefIds
    from ..models.big_plan_update_args_difficulty import BigPlanUpdateArgsDifficulty
    from ..models.big_plan_update_args_due_date import BigPlanUpdateArgsDueDate
    from ..models.big_plan_update_args_eisen import BigPlanUpdateArgsEisen
    from ..models.big_plan_update_args_goal_ref_id import BigPlanUpdateArgsGoalRefId
    from ..models.big_plan_update_args_is_key import BigPlanUpdateArgsIsKey
    from ..models.big_plan_update_args_name import BigPlanUpdateArgsName
    from ..models.big_plan_update_args_schedulability import BigPlanUpdateArgsSchedulability
    from ..models.big_plan_update_args_scheduling_event_count import BigPlanUpdateArgsSchedulingEventCount
    from ..models.big_plan_update_args_scheduling_event_duration_mins import (
        BigPlanUpdateArgsSchedulingEventDurationMins,
    )
    from ..models.big_plan_update_args_status import BigPlanUpdateArgsStatus


T = TypeVar("T", bound="BigPlanUpdateArgs")


@_attrs_define
class BigPlanUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (BigPlanUpdateArgsName):
        status (BigPlanUpdateArgsStatus):
        aspect_ref_id (BigPlanUpdateArgsAspectRefId):
        chapter_ref_id (BigPlanUpdateArgsChapterRefId):
        goal_ref_id (BigPlanUpdateArgsGoalRefId):
        is_key (BigPlanUpdateArgsIsKey):
        eisen (BigPlanUpdateArgsEisen):
        difficulty (BigPlanUpdateArgsDifficulty):
        actionable_date (BigPlanUpdateArgsActionableDate):
        due_date (BigPlanUpdateArgsDueDate):
        schedulability (BigPlanUpdateArgsSchedulability):
        scheduling_event_duration_mins (BigPlanUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (BigPlanUpdateArgsSchedulingEventCount):
        dependency_ref_ids (BigPlanUpdateArgsDependencyRefIds):
    """

    ref_id: str
    name: BigPlanUpdateArgsName
    status: BigPlanUpdateArgsStatus
    aspect_ref_id: BigPlanUpdateArgsAspectRefId
    chapter_ref_id: BigPlanUpdateArgsChapterRefId
    goal_ref_id: BigPlanUpdateArgsGoalRefId
    is_key: BigPlanUpdateArgsIsKey
    eisen: BigPlanUpdateArgsEisen
    difficulty: BigPlanUpdateArgsDifficulty
    actionable_date: BigPlanUpdateArgsActionableDate
    due_date: BigPlanUpdateArgsDueDate
    schedulability: BigPlanUpdateArgsSchedulability
    scheduling_event_duration_mins: BigPlanUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: BigPlanUpdateArgsSchedulingEventCount
    dependency_ref_ids: BigPlanUpdateArgsDependencyRefIds
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        status = self.status.to_dict()

        aspect_ref_id = self.aspect_ref_id.to_dict()

        chapter_ref_id = self.chapter_ref_id.to_dict()

        goal_ref_id = self.goal_ref_id.to_dict()

        is_key = self.is_key.to_dict()

        eisen = self.eisen.to_dict()

        difficulty = self.difficulty.to_dict()

        actionable_date = self.actionable_date.to_dict()

        due_date = self.due_date.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        dependency_ref_ids = self.dependency_ref_ids.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "status": status,
                "aspect_ref_id": aspect_ref_id,
                "chapter_ref_id": chapter_ref_id,
                "goal_ref_id": goal_ref_id,
                "is_key": is_key,
                "eisen": eisen,
                "difficulty": difficulty,
                "actionable_date": actionable_date,
                "due_date": due_date,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
                "dependency_ref_ids": dependency_ref_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan_update_args_actionable_date import BigPlanUpdateArgsActionableDate  # noqa: PLC0415
        from ..models.big_plan_update_args_aspect_ref_id import BigPlanUpdateArgsAspectRefId  # noqa: PLC0415
        from ..models.big_plan_update_args_chapter_ref_id import BigPlanUpdateArgsChapterRefId  # noqa: PLC0415
        from ..models.big_plan_update_args_dependency_ref_ids import BigPlanUpdateArgsDependencyRefIds  # noqa: PLC0415
        from ..models.big_plan_update_args_difficulty import BigPlanUpdateArgsDifficulty  # noqa: PLC0415
        from ..models.big_plan_update_args_due_date import BigPlanUpdateArgsDueDate  # noqa: PLC0415
        from ..models.big_plan_update_args_eisen import BigPlanUpdateArgsEisen  # noqa: PLC0415
        from ..models.big_plan_update_args_goal_ref_id import BigPlanUpdateArgsGoalRefId  # noqa: PLC0415
        from ..models.big_plan_update_args_is_key import BigPlanUpdateArgsIsKey  # noqa: PLC0415
        from ..models.big_plan_update_args_name import BigPlanUpdateArgsName  # noqa: PLC0415
        from ..models.big_plan_update_args_schedulability import BigPlanUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.big_plan_update_args_scheduling_event_count import BigPlanUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.big_plan_update_args_scheduling_event_duration_mins import (
            BigPlanUpdateArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )
        from ..models.big_plan_update_args_status import BigPlanUpdateArgsStatus  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = BigPlanUpdateArgsName.from_dict(d.pop("name"))

        status = BigPlanUpdateArgsStatus.from_dict(d.pop("status"))

        aspect_ref_id = BigPlanUpdateArgsAspectRefId.from_dict(d.pop("aspect_ref_id"))

        chapter_ref_id = BigPlanUpdateArgsChapterRefId.from_dict(d.pop("chapter_ref_id"))

        goal_ref_id = BigPlanUpdateArgsGoalRefId.from_dict(d.pop("goal_ref_id"))

        is_key = BigPlanUpdateArgsIsKey.from_dict(d.pop("is_key"))

        eisen = BigPlanUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = BigPlanUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_date = BigPlanUpdateArgsActionableDate.from_dict(d.pop("actionable_date"))

        due_date = BigPlanUpdateArgsDueDate.from_dict(d.pop("due_date"))

        schedulability = BigPlanUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = BigPlanUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = BigPlanUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        dependency_ref_ids = BigPlanUpdateArgsDependencyRefIds.from_dict(d.pop("dependency_ref_ids"))

        big_plan_update_args = cls(
            ref_id=ref_id,
            name=name,
            status=status,
            aspect_ref_id=aspect_ref_id,
            chapter_ref_id=chapter_ref_id,
            goal_ref_id=goal_ref_id,
            is_key=is_key,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
            dependency_ref_ids=dependency_ref_ids,
        )

        big_plan_update_args.additional_properties = d
        return big_plan_update_args

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
