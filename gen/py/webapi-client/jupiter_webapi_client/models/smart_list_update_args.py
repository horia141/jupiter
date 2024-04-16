from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_update_args_icon import SmartListUpdateArgsIcon
    from ..models.smart_list_update_args_name import SmartListUpdateArgsName


T = TypeVar("T", bound="SmartListUpdateArgs")


@_attrs_define
class SmartListUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (SmartListUpdateArgsName):
        icon (SmartListUpdateArgsIcon):
    """

    ref_id: str
    name: "SmartListUpdateArgsName"
    icon: "SmartListUpdateArgsIcon"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        icon = self.icon.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "icon": icon,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.smart_list_update_args_icon import SmartListUpdateArgsIcon
        from ..models.smart_list_update_args_name import SmartListUpdateArgsName

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = SmartListUpdateArgsName.from_dict(d.pop("name"))

        icon = SmartListUpdateArgsIcon.from_dict(d.pop("icon"))

        smart_list_update_args = cls(
            ref_id=ref_id,
            name=name,
            icon=icon,
        )

        smart_list_update_args.additional_properties = d
        return smart_list_update_args

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
