from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VacationCreateArgs")


@_attrs_define
class VacationCreateArgs:
    """Vacation creation parameters.

    Attributes:
        name (str): The vacation name.
        start_date (str): A date or possibly a datetime for the application.
        end_date (str): A date or possibly a datetime for the application.
    """

    name: str
    start_date: str
    end_date: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        start_date = self.start_date

        end_date = self.end_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        start_date = d.pop("start_date")

        end_date = d.pop("end_date")

        vacation_create_args = cls(
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        vacation_create_args.additional_properties = d
        return vacation_create_args

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
