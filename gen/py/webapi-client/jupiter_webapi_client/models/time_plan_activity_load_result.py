from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.inbox_task import InboxTask
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanActivityLoadResult")


@_attrs_define
class TimePlanActivityLoadResult:
    """TimePlanActivityLoadResult.

    Attributes:
        time_plan_activity (TimePlanActivity): A certain activity that happens in a plan.
        target_inbox_task (Union['InboxTask', None, Unset]):
        target_big_plan (Union['BigPlan', None, Unset]):
    """

    time_plan_activity: "TimePlanActivity"
    target_inbox_task: Union["InboxTask", None, Unset] = UNSET
    target_big_plan: Union["BigPlan", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.big_plan import BigPlan
        from ..models.inbox_task import InboxTask

        time_plan_activity = self.time_plan_activity.to_dict()

        target_inbox_task: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_inbox_task, Unset):
            target_inbox_task = UNSET
        elif isinstance(self.target_inbox_task, InboxTask):
            target_inbox_task = self.target_inbox_task.to_dict()
        else:
            target_inbox_task = self.target_inbox_task

        target_big_plan: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_big_plan, Unset):
            target_big_plan = UNSET
        elif isinstance(self.target_big_plan, BigPlan):
            target_big_plan = self.target_big_plan.to_dict()
        else:
            target_big_plan = self.target_big_plan

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan_activity": time_plan_activity,
            }
        )
        if target_inbox_task is not UNSET:
            field_dict["target_inbox_task"] = target_inbox_task
        if target_big_plan is not UNSET:
            field_dict["target_big_plan"] = target_big_plan

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.inbox_task import InboxTask
        from ..models.time_plan_activity import TimePlanActivity

        d = dict(src_dict)
        time_plan_activity = TimePlanActivity.from_dict(d.pop("time_plan_activity"))

        def _parse_target_inbox_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_inbox_task_type_0 = InboxTask.from_dict(data)

                return target_inbox_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        target_inbox_task = _parse_target_inbox_task(d.pop("target_inbox_task", UNSET))

        def _parse_target_big_plan(data: object) -> Union["BigPlan", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_big_plan_type_0 = BigPlan.from_dict(data)

                return target_big_plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union["BigPlan", None, Unset], data)

        target_big_plan = _parse_target_big_plan(d.pop("target_big_plan", UNSET))

        time_plan_activity_load_result = cls(
            time_plan_activity=time_plan_activity,
            target_inbox_task=target_inbox_task,
            target_big_plan=target_big_plan,
        )

        time_plan_activity_load_result.additional_properties = d
        return time_plan_activity_load_result

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
