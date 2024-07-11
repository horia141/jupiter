from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.person import Person
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock


T = TypeVar("T", bound="PersonEntry")


@_attrs_define
class PersonEntry:
    """Result entry.

    Attributes:
        person (Person): A person.
        birthday_time_event (TimeEventFullDaysBlock): A full day block of time.
    """

    person: "Person"
    birthday_time_event: "TimeEventFullDaysBlock"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        person = self.person.to_dict()

        birthday_time_event = self.birthday_time_event.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person": person,
                "birthday_time_event": birthday_time_event,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.person import Person
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock

        d = src_dict.copy()
        person = Person.from_dict(d.pop("person"))

        birthday_time_event = TimeEventFullDaysBlock.from_dict(d.pop("birthday_time_event"))

        person_entry = cls(
            person=person,
            birthday_time_event=birthday_time_event,
        )

        person_entry.additional_properties = d
        return person_entry

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
