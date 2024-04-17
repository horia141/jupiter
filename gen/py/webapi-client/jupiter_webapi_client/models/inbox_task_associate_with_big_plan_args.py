from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InboxTaskAssociateWithBigPlanArgs")


@_attrs_define
class InboxTaskAssociateWithBigPlanArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        big_plan_ref_id (Union[None, Unset, str]):
    """

    ref_id: str
    big_plan_ref_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        big_plan_ref_id: Union[None, Unset, str]
        if isinstance(self.big_plan_ref_id, Unset):
            big_plan_ref_id = UNSET
        else:
            big_plan_ref_id = self.big_plan_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
            }
        )
        if big_plan_ref_id is not UNSET:
            field_dict["big_plan_ref_id"] = big_plan_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        def _parse_big_plan_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        big_plan_ref_id = _parse_big_plan_ref_id(d.pop("big_plan_ref_id", UNSET))

        inbox_task_associate_with_big_plan_args = cls(
            ref_id=ref_id,
            big_plan_ref_id=big_plan_ref_id,
        )

        inbox_task_associate_with_big_plan_args.additional_properties = d
        return inbox_task_associate_with_big_plan_args

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
