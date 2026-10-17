from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_change_time_config_args_aspect_ref_ids import TimePlanChangeTimeConfigArgsAspectRefIds
    from ..models.time_plan_change_time_config_args_chapter_ref_ids import TimePlanChangeTimeConfigArgsChapterRefIds
    from ..models.time_plan_change_time_config_args_goal_ref_ids import TimePlanChangeTimeConfigArgsGoalRefIds
    from ..models.time_plan_change_time_config_args_period import TimePlanChangeTimeConfigArgsPeriod
    from ..models.time_plan_change_time_config_args_right_now import TimePlanChangeTimeConfigArgsRightNow


T = TypeVar("T", bound="TimePlanChangeTimeConfigArgs")


@_attrs_define
class TimePlanChangeTimeConfigArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        right_now (TimePlanChangeTimeConfigArgsRightNow):
        period (TimePlanChangeTimeConfigArgsPeriod):
        chapter_ref_ids (TimePlanChangeTimeConfigArgsChapterRefIds):
        aspect_ref_ids (TimePlanChangeTimeConfigArgsAspectRefIds):
        goal_ref_ids (TimePlanChangeTimeConfigArgsGoalRefIds):
    """

    ref_id: str
    right_now: TimePlanChangeTimeConfigArgsRightNow
    period: TimePlanChangeTimeConfigArgsPeriod
    chapter_ref_ids: TimePlanChangeTimeConfigArgsChapterRefIds
    aspect_ref_ids: TimePlanChangeTimeConfigArgsAspectRefIds
    goal_ref_ids: TimePlanChangeTimeConfigArgsGoalRefIds
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        right_now = self.right_now.to_dict()

        period = self.period.to_dict()

        chapter_ref_ids = self.chapter_ref_ids.to_dict()

        aspect_ref_ids = self.aspect_ref_ids.to_dict()

        goal_ref_ids = self.goal_ref_ids.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "right_now": right_now,
                "period": period,
                "chapter_ref_ids": chapter_ref_ids,
                "aspect_ref_ids": aspect_ref_ids,
                "goal_ref_ids": goal_ref_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_plan_change_time_config_args_aspect_ref_ids import TimePlanChangeTimeConfigArgsAspectRefIds  # noqa: PLC0415
        from ..models.time_plan_change_time_config_args_chapter_ref_ids import TimePlanChangeTimeConfigArgsChapterRefIds  # noqa: PLC0415
        from ..models.time_plan_change_time_config_args_goal_ref_ids import TimePlanChangeTimeConfigArgsGoalRefIds  # noqa: PLC0415
        from ..models.time_plan_change_time_config_args_period import TimePlanChangeTimeConfigArgsPeriod  # noqa: PLC0415
        from ..models.time_plan_change_time_config_args_right_now import TimePlanChangeTimeConfigArgsRightNow  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        right_now = TimePlanChangeTimeConfigArgsRightNow.from_dict(d.pop("right_now"))

        period = TimePlanChangeTimeConfigArgsPeriod.from_dict(d.pop("period"))

        chapter_ref_ids = TimePlanChangeTimeConfigArgsChapterRefIds.from_dict(d.pop("chapter_ref_ids"))

        aspect_ref_ids = TimePlanChangeTimeConfigArgsAspectRefIds.from_dict(d.pop("aspect_ref_ids"))

        goal_ref_ids = TimePlanChangeTimeConfigArgsGoalRefIds.from_dict(d.pop("goal_ref_ids"))

        time_plan_change_time_config_args = cls(
            ref_id=ref_id,
            right_now=right_now,
            period=period,
            chapter_ref_ids=chapter_ref_ids,
            aspect_ref_ids=aspect_ref_ids,
            goal_ref_ids=goal_ref_ids,
        )

        time_plan_change_time_config_args.additional_properties = d
        return time_plan_change_time_config_args

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
