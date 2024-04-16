from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vacation import Vacation


T = TypeVar("T", bound="VacationCreateResult")


@_attrs_define
class VacationCreateResult:
    """Vacation creation result.

    Attributes:
        new_vacation (Vacation): A vacation.
    """

    new_vacation: "Vacation"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_vacation = self.new_vacation.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_vacation": new_vacation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.vacation import Vacation

        d = src_dict.copy()
        new_vacation = Vacation.from_dict(d.pop("new_vacation"))

        vacation_create_result = cls(
            new_vacation=new_vacation,
        )

        vacation_create_result.additional_properties = d
        return vacation_create_result

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
