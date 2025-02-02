from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.inbox_task_status import InboxTaskStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="PushGenerationExtraInfo")


@_attrs_define
class PushGenerationExtraInfo:
    """Extra information for how to generate an inbox task.

    Attributes:
        timezone (str): A timezone in this domain.
        eisen (Eisen): The Eisenhower status of a particular task.
        difficulty (Difficulty): The difficulty of a particular task.
        name (Union[None, Unset, str]):
        status (Union[InboxTaskStatus, None, Unset]):
        actionable_date (Union[None, Unset, str]):
        due_date (Union[None, Unset, str]):
    """

    timezone: str
    eisen: Eisen
    difficulty: Difficulty
    name: Union[None, Unset, str] = UNSET
    status: Union[InboxTaskStatus, None, Unset] = UNSET
    actionable_date: Union[None, Unset, str] = UNSET
    due_date: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timezone = self.timezone

        eisen = self.eisen.value

        difficulty = self.difficulty.value

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, InboxTaskStatus):
            status = self.status.value
        else:
            status = self.status

        actionable_date: Union[None, Unset, str]
        if isinstance(self.actionable_date, Unset):
            actionable_date = UNSET
        else:
            actionable_date = self.actionable_date

        due_date: Union[None, Unset, str]
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timezone": timezone,
                "eisen": eisen,
                "difficulty": difficulty,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date
        if due_date is not UNSET:
            field_dict["due_date"] = due_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        timezone = d.pop("timezone")

        eisen = Eisen(d.pop("eisen"))

        difficulty = Difficulty(d.pop("difficulty"))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_status(data: object) -> Union[InboxTaskStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = InboxTaskStatus(data)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[InboxTaskStatus, None, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_actionable_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        actionable_date = _parse_actionable_date(d.pop("actionable_date", UNSET))

        def _parse_due_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        push_generation_extra_info = cls(
            timezone=timezone,
            eisen=eisen,
            difficulty=difficulty,
            name=name,
            status=status,
            actionable_date=actionable_date,
            due_date=due_date,
        )

        push_generation_extra_info.additional_properties = d
        return push_generation_extra_info

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
