from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vacation_update_args_end_date import VacationUpdateArgsEndDate
    from ..models.vacation_update_args_name import VacationUpdateArgsName
    from ..models.vacation_update_args_start_date import VacationUpdateArgsStartDate


T = TypeVar("T", bound="VacationUpdateArgs")


@_attrs_define
class VacationUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (VacationUpdateArgsName):
        start_date (VacationUpdateArgsStartDate):
        end_date (VacationUpdateArgsEndDate):
    """

    ref_id: str
    name: "VacationUpdateArgsName"
    start_date: "VacationUpdateArgsStartDate"
    end_date: "VacationUpdateArgsEndDate"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        start_date = self.start_date.to_dict()

        end_date = self.end_date.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.vacation_update_args_end_date import VacationUpdateArgsEndDate
        from ..models.vacation_update_args_name import VacationUpdateArgsName
        from ..models.vacation_update_args_start_date import VacationUpdateArgsStartDate

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = VacationUpdateArgsName.from_dict(d.pop("name"))

        start_date = VacationUpdateArgsStartDate.from_dict(d.pop("start_date"))

        end_date = VacationUpdateArgsEndDate.from_dict(d.pop("end_date"))

        vacation_update_args = cls(
            ref_id=ref_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        vacation_update_args.additional_properties = d
        return vacation_update_args

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
