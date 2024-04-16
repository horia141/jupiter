from typing import Any, Dict, List, Type, TypeVar, Union

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
        name (Union[Unset, str]): The name of an inbox task.
        status (Union[Unset, InboxTaskStatus]): The status of an inbox task.
        eisen (Union[Unset, Eisen]): The Eisenhower status of a particular task.
        difficulty (Union[Unset, Difficulty]): The difficulty of a particular task.
        actionable_date (Union[Unset, str]): A date or possibly a datetime for the application.
        due_date (Union[Unset, str]): A date or possibly a datetime for the application.
    """

    timezone: str
    name: Union[Unset, str] = UNSET
    status: Union[Unset, InboxTaskStatus] = UNSET
    eisen: Union[Unset, Eisen] = UNSET
    difficulty: Union[Unset, Difficulty] = UNSET
    actionable_date: Union[Unset, str] = UNSET
    due_date: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timezone = self.timezone

        name = self.name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        eisen: Union[Unset, str] = UNSET
        if not isinstance(self.eisen, Unset):
            eisen = self.eisen.value

        difficulty: Union[Unset, str] = UNSET
        if not isinstance(self.difficulty, Unset):
            difficulty = self.difficulty.value

        actionable_date = self.actionable_date

        due_date = self.due_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timezone": timezone,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if eisen is not UNSET:
            field_dict["eisen"] = eisen
        if difficulty is not UNSET:
            field_dict["difficulty"] = difficulty
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date
        if due_date is not UNSET:
            field_dict["due_date"] = due_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        timezone = d.pop("timezone")

        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, InboxTaskStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = InboxTaskStatus(_status)

        _eisen = d.pop("eisen", UNSET)
        eisen: Union[Unset, Eisen]
        if isinstance(_eisen, Unset):
            eisen = UNSET
        else:
            eisen = Eisen(_eisen)

        _difficulty = d.pop("difficulty", UNSET)
        difficulty: Union[Unset, Difficulty]
        if isinstance(_difficulty, Unset):
            difficulty = UNSET
        else:
            difficulty = Difficulty(_difficulty)

        actionable_date = d.pop("actionable_date", UNSET)

        due_date = d.pop("due_date", UNSET)

        push_generation_extra_info = cls(
            timezone=timezone,
            name=name,
            status=status,
            eisen=eisen,
            difficulty=difficulty,
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
