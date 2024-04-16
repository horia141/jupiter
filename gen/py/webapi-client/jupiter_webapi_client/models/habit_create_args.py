from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="HabitCreateArgs")


@_attrs_define
class HabitCreateArgs:
    """HabitCreate args..

    Attributes:
        name (str): The habit name.
        period (RecurringTaskPeriod): A period for a particular task.
        project_ref_id (Union[Unset, str]): A generic entity id.
        eisen (Union[Unset, Eisen]): The Eisenhower status of a particular task.
        difficulty (Union[Unset, Difficulty]): The difficulty of a particular task.
        actionable_from_day (Union[Unset, int]): The due day for a recurring task.
        actionable_from_month (Union[Unset, int]): The due month for a recurring task.
        due_at_day (Union[Unset, int]): The due day for a recurring task.
        due_at_month (Union[Unset, int]): The due month for a recurring task.
        skip_rule (Union[Unset, str]): The rules for skipping a recurring task.
        repeats_in_period_count (Union[Unset, int]):
    """

    name: str
    period: RecurringTaskPeriod
    project_ref_id: Union[Unset, str] = UNSET
    eisen: Union[Unset, Eisen] = UNSET
    difficulty: Union[Unset, Difficulty] = UNSET
    actionable_from_day: Union[Unset, int] = UNSET
    actionable_from_month: Union[Unset, int] = UNSET
    due_at_day: Union[Unset, int] = UNSET
    due_at_month: Union[Unset, int] = UNSET
    skip_rule: Union[Unset, str] = UNSET
    repeats_in_period_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        period = self.period.value

        project_ref_id = self.project_ref_id

        eisen: Union[Unset, str] = UNSET
        if not isinstance(self.eisen, Unset):
            eisen = self.eisen.value

        difficulty: Union[Unset, str] = UNSET
        if not isinstance(self.difficulty, Unset):
            difficulty = self.difficulty.value

        actionable_from_day = self.actionable_from_day

        actionable_from_month = self.actionable_from_month

        due_at_day = self.due_at_day

        due_at_month = self.due_at_month

        skip_rule = self.skip_rule

        repeats_in_period_count = self.repeats_in_period_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "period": period,
            }
        )
        if project_ref_id is not UNSET:
            field_dict["project_ref_id"] = project_ref_id
        if eisen is not UNSET:
            field_dict["eisen"] = eisen
        if difficulty is not UNSET:
            field_dict["difficulty"] = difficulty
        if actionable_from_day is not UNSET:
            field_dict["actionable_from_day"] = actionable_from_day
        if actionable_from_month is not UNSET:
            field_dict["actionable_from_month"] = actionable_from_month
        if due_at_day is not UNSET:
            field_dict["due_at_day"] = due_at_day
        if due_at_month is not UNSET:
            field_dict["due_at_month"] = due_at_month
        if skip_rule is not UNSET:
            field_dict["skip_rule"] = skip_rule
        if repeats_in_period_count is not UNSET:
            field_dict["repeats_in_period_count"] = repeats_in_period_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        period = RecurringTaskPeriod(d.pop("period"))

        project_ref_id = d.pop("project_ref_id", UNSET)

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

        actionable_from_day = d.pop("actionable_from_day", UNSET)

        actionable_from_month = d.pop("actionable_from_month", UNSET)

        due_at_day = d.pop("due_at_day", UNSET)

        due_at_month = d.pop("due_at_month", UNSET)

        skip_rule = d.pop("skip_rule", UNSET)

        repeats_in_period_count = d.pop("repeats_in_period_count", UNSET)

        habit_create_args = cls(
            name=name,
            period=period,
            project_ref_id=project_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            repeats_in_period_count=repeats_in_period_count,
        )

        habit_create_args.additional_properties = d
        return habit_create_args

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
