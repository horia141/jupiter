from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.note import Note
    from ..models.schedule_event_full_days import ScheduleEventFullDays
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock


T = TypeVar("T", bound="ScheduleEventFullDaysLoadResult")


@_attrs_define
class ScheduleEventFullDaysLoadResult:
    """Result.

    Attributes:
        schedule_event_full_days (ScheduleEventFullDays): A full day block in a schedule.
        time_event_full_days_block (TimeEventFullDaysBlock): A full day block of time.
        note (Union['Note', None, Unset]):
    """

    schedule_event_full_days: "ScheduleEventFullDays"
    time_event_full_days_block: "TimeEventFullDaysBlock"
    note: Union["Note", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.note import Note

        schedule_event_full_days = self.schedule_event_full_days.to_dict()

        time_event_full_days_block = self.time_event_full_days_block.to_dict()

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedule_event_full_days": schedule_event_full_days,
                "time_event_full_days_block": time_event_full_days_block,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.note import Note
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock

        d = src_dict.copy()
        schedule_event_full_days = ScheduleEventFullDays.from_dict(d.pop("schedule_event_full_days"))

        time_event_full_days_block = TimeEventFullDaysBlock.from_dict(d.pop("time_event_full_days_block"))

        def _parse_note(data: object) -> Union["Note", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Note", None, Unset], data)

        note = _parse_note(d.pop("note", UNSET))

        schedule_event_full_days_load_result = cls(
            schedule_event_full_days=schedule_event_full_days,
            time_event_full_days_block=time_event_full_days_block,
            note=note,
        )

        schedule_event_full_days_load_result.additional_properties = d
        return schedule_event_full_days_load_result

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
