from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..types import UNSET, Unset

T = TypeVar("T", bound="InboxTaskCreateArgs")


@_attrs_define
class InboxTaskCreateArgs:
    """InboxTaskCreate args.

    Attributes:
        name (str): The name of an inbox task.
        project_ref_id (Union[None, Unset, str]):
        big_plan_ref_id (Union[None, Unset, str]):
        eisen (Union[Eisen, None, Unset]):
        difficulty (Union[Difficulty, None, Unset]):
        actionable_date (Union[None, Unset, str]):
        due_date (Union[None, Unset, str]):
    """

    name: str
    project_ref_id: Union[None, Unset, str] = UNSET
    big_plan_ref_id: Union[None, Unset, str] = UNSET
    eisen: Union[Eisen, None, Unset] = UNSET
    difficulty: Union[Difficulty, None, Unset] = UNSET
    actionable_date: Union[None, Unset, str] = UNSET
    due_date: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        project_ref_id: Union[None, Unset, str]
        if isinstance(self.project_ref_id, Unset):
            project_ref_id = UNSET
        else:
            project_ref_id = self.project_ref_id

        big_plan_ref_id: Union[None, Unset, str]
        if isinstance(self.big_plan_ref_id, Unset):
            big_plan_ref_id = UNSET
        else:
            big_plan_ref_id = self.big_plan_ref_id

        eisen: Union[None, Unset, str]
        if isinstance(self.eisen, Unset):
            eisen = UNSET
        elif isinstance(self.eisen, Eisen):
            eisen = self.eisen.value
        else:
            eisen = self.eisen

        difficulty: Union[None, Unset, str]
        if isinstance(self.difficulty, Unset):
            difficulty = UNSET
        elif isinstance(self.difficulty, Difficulty):
            difficulty = self.difficulty.value
        else:
            difficulty = self.difficulty

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
                "name": name,
            }
        )
        if project_ref_id is not UNSET:
            field_dict["project_ref_id"] = project_ref_id
        if big_plan_ref_id is not UNSET:
            field_dict["big_plan_ref_id"] = big_plan_ref_id
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
        name = d.pop("name")

        def _parse_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_ref_id = _parse_project_ref_id(d.pop("project_ref_id", UNSET))

        def _parse_big_plan_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        big_plan_ref_id = _parse_big_plan_ref_id(d.pop("big_plan_ref_id", UNSET))

        def _parse_eisen(data: object) -> Union[Eisen, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                eisen_type_0 = Eisen(data)

                return eisen_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Eisen, None, Unset], data)

        eisen = _parse_eisen(d.pop("eisen", UNSET))

        def _parse_difficulty(data: object) -> Union[Difficulty, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                difficulty_type_0 = Difficulty(data)

                return difficulty_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Difficulty, None, Unset], data)

        difficulty = _parse_difficulty(d.pop("difficulty", UNSET))

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

        inbox_task_create_args = cls(
            name=name,
            project_ref_id=project_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
        )

        inbox_task_create_args.additional_properties = d
        return inbox_task_create_args

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
