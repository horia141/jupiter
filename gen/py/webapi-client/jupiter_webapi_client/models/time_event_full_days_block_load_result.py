from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.person import Person
    from ..models.schedule_event_full_days import ScheduleEventFullDays
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock
    from ..models.vacation import Vacation


T = TypeVar("T", bound="TimeEventFullDaysBlockLoadResult")


@_attrs_define
class TimeEventFullDaysBlockLoadResult:
    """FullDaysBlockLoadResult.

    Attributes:
        full_days_block (TimeEventFullDaysBlock): A full day block of time.
        schedule_event (Union['ScheduleEventFullDays', None, Unset]):
        person (Union['Person', None, Unset]):
        vacation (Union['Vacation', None, Unset]):
    """

    full_days_block: "TimeEventFullDaysBlock"
    schedule_event: Union["ScheduleEventFullDays", None, Unset] = UNSET
    person: Union["Person", None, Unset] = UNSET
    vacation: Union["Vacation", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.person import Person
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.vacation import Vacation

        full_days_block = self.full_days_block.to_dict()

        schedule_event: Union[None, Unset, dict[str, Any]]
        if isinstance(self.schedule_event, Unset):
            schedule_event = UNSET
        elif isinstance(self.schedule_event, ScheduleEventFullDays):
            schedule_event = self.schedule_event.to_dict()
        else:
            schedule_event = self.schedule_event

        person: Union[None, Unset, dict[str, Any]]
        if isinstance(self.person, Unset):
            person = UNSET
        elif isinstance(self.person, Person):
            person = self.person.to_dict()
        else:
            person = self.person

        vacation: Union[None, Unset, dict[str, Any]]
        if isinstance(self.vacation, Unset):
            vacation = UNSET
        elif isinstance(self.vacation, Vacation):
            vacation = self.vacation.to_dict()
        else:
            vacation = self.vacation

        field_dict: dict[str, Any] = {}
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
        if vacation is not UNSET:
            field_dict["vacation"] = vacation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.person import Person
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock
        from ..models.vacation import Vacation

        d = dict(src_dict)
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

        def _parse_vacation(data: object) -> Union["Vacation", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                vacation_type_0 = Vacation.from_dict(data)

                return vacation_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Vacation", None, Unset], data)

        vacation = _parse_vacation(d.pop("vacation", UNSET))

        time_event_full_days_block_load_result = cls(
            full_days_block=full_days_block,
            schedule_event=schedule_event,
            person=person,
            vacation=vacation,
        )

        time_event_full_days_block_load_result.additional_properties = d
        return time_event_full_days_block_load_result

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
