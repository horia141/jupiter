from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_activity_update_args_feasability import TimePlanActivityUpdateArgsFeasability
    from ..models.time_plan_activity_update_args_kind import TimePlanActivityUpdateArgsKind


T = TypeVar("T", bound="TimePlanActivityUpdateArgs")


@_attrs_define
class TimePlanActivityUpdateArgs:
    """TimePlanActivityFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        kind (TimePlanActivityUpdateArgsKind):
        feasability (TimePlanActivityUpdateArgsFeasability):
    """

    ref_id: str
    kind: "TimePlanActivityUpdateArgsKind"
    feasability: "TimePlanActivityUpdateArgsFeasability"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        kind = self.kind.to_dict()

        feasability = self.feasability.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "kind": kind,
                "feasability": feasability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_plan_activity_update_args_feasability import TimePlanActivityUpdateArgsFeasability
        from ..models.time_plan_activity_update_args_kind import TimePlanActivityUpdateArgsKind

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        kind = TimePlanActivityUpdateArgsKind.from_dict(d.pop("kind"))

        feasability = TimePlanActivityUpdateArgsFeasability.from_dict(d.pop("feasability"))

        time_plan_activity_update_args = cls(
            ref_id=ref_id,
            kind=kind,
            feasability=feasability,
        )

        time_plan_activity_update_args.additional_properties = d
        return time_plan_activity_update_args

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
