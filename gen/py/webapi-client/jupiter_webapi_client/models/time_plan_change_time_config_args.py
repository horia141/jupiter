from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
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
    """

    ref_id: str
    right_now: "TimePlanChangeTimeConfigArgsRightNow"
    period: "TimePlanChangeTimeConfigArgsPeriod"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        right_now = self.right_now.to_dict()

        period = self.period.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "right_now": right_now,
                "period": period,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_plan_change_time_config_args_period import TimePlanChangeTimeConfigArgsPeriod
        from ..models.time_plan_change_time_config_args_right_now import TimePlanChangeTimeConfigArgsRightNow

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        right_now = TimePlanChangeTimeConfigArgsRightNow.from_dict(d.pop("right_now"))

        period = TimePlanChangeTimeConfigArgsPeriod.from_dict(d.pop("period"))

        time_plan_change_time_config_args = cls(
            ref_id=ref_id,
            right_now=right_now,
            period=period,
        )

        time_plan_change_time_config_args.additional_properties = d
        return time_plan_change_time_config_args

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
