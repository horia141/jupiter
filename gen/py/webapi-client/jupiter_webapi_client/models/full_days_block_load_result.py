from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.person import Person
    from ..models.schedule_event_full_days import ScheduleEventFullDays
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock


T = TypeVar("T", bound="FullDaysBlockLoadResult")


@_attrs_define
class FullDaysBlockLoadResult:
    """FullDaysBlockLoadResult.

    Attributes:
        full_days_block (TimeEventFullDaysBlock): A full day block of time.
        schedule_event (Union['ScheduleEventFullDays', None, Unset]):
        person (Union['Person', None, Unset]):
    """

    full_days_block: "TimeEventFullDaysBlock"
    schedule_event: Union["ScheduleEventFullDays", None, Unset] = UNSET
    person: Union["Person", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.person import Person
        from ..models.schedule_event_full_days import ScheduleEventFullDays

        full_days_block = self.full_days_block.to_dict()

        schedule_event: Union[Dict[str, Any], None, Unset]
        if isinstance(self.schedule_event, Unset):
            schedule_event = UNSET
        elif isinstance(self.schedule_event, ScheduleEventFullDays):
            schedule_event = self.schedule_event.to_dict()
        else:
            schedule_event = self.schedule_event

        person: Union[Dict[str, Any], None, Unset]
        if isinstance(self.person, Unset):
            person = UNSET
        elif isinstance(self.person, Person):
            person = self.person.to_dict()
        else:
            person = self.person

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "full_days_block": full_days_block,
            }
        )
        if schedule_event is not UNSET:
            field_dict["schedule_event"] = schedule_event
        if person is not UNSET:
            field_dict["person"] = person

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.person import Person
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock

        d = src_dict.copy()
        full_days_block = TimeEventFullDaysBlock.from_dict(d.pop("full_days_block"))

        def _parse_schedule_event(data: object) -> Union["ScheduleEventFullDays", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schedule_event_type_0 = ScheduleEventFullDays.from_dict(data)

                return schedule_event_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ScheduleEventFullDays", None, Unset], data)

        schedule_event = _parse_schedule_event(d.pop("schedule_event", UNSET))

        def _parse_person(data: object) -> Union["Person", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                person_type_0 = Person.from_dict(data)

                return person_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Person", None, Unset], data)

        person = _parse_person(d.pop("person", UNSET))

        full_days_block_load_result = cls(
            full_days_block=full_days_block,
            schedule_event=schedule_event,
            person=person,
        )

        full_days_block_load_result.additional_properties = d
        return full_days_block_load_result

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
