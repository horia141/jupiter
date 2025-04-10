from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.habit_repeats_strategy import HabitRepeatsStrategy
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="HabitCreateArgs")


@_attrs_define
class HabitCreateArgs:
    """HabitCreate args..

    Attributes:
        name (str): The habit name.
        period (RecurringTaskPeriod): A period for a particular task.
        eisen (Eisen): The Eisenhower status of a particular task.
        difficulty (Difficulty): The difficulty of a particular task.
        project_ref_id (Union[None, Unset, str]):
        actionable_from_day (Union[None, Unset, int]):
        actionable_from_month (Union[None, Unset, int]):
        due_at_day (Union[None, Unset, int]):
        due_at_month (Union[None, Unset, int]):
        skip_rule (Union[None, Unset, str]):
        repeats_strategy (Union[HabitRepeatsStrategy, None, Unset]):
        repeats_in_period_count (Union[None, Unset, int]):
    """

    name: str
    period: RecurringTaskPeriod
    eisen: Eisen
    difficulty: Difficulty
    project_ref_id: Union[None, Unset, str] = UNSET
    actionable_from_day: Union[None, Unset, int] = UNSET
    actionable_from_month: Union[None, Unset, int] = UNSET
    due_at_day: Union[None, Unset, int] = UNSET
    due_at_month: Union[None, Unset, int] = UNSET
    skip_rule: Union[None, Unset, str] = UNSET
    repeats_strategy: Union[HabitRepeatsStrategy, None, Unset] = UNSET
    repeats_in_period_count: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        period = self.period.value

        eisen = self.eisen.value

        difficulty = self.difficulty.value

        project_ref_id: Union[None, Unset, str]
        if isinstance(self.project_ref_id, Unset):
            project_ref_id = UNSET
        else:
            project_ref_id = self.project_ref_id

        actionable_from_day: Union[None, Unset, int]
        if isinstance(self.actionable_from_day, Unset):
            actionable_from_day = UNSET
        else:
            actionable_from_day = self.actionable_from_day

        actionable_from_month: Union[None, Unset, int]
        if isinstance(self.actionable_from_month, Unset):
            actionable_from_month = UNSET
        else:
            actionable_from_month = self.actionable_from_month

        due_at_day: Union[None, Unset, int]
        if isinstance(self.due_at_day, Unset):
            due_at_day = UNSET
        else:
            due_at_day = self.due_at_day

        due_at_month: Union[None, Unset, int]
        if isinstance(self.due_at_month, Unset):
            due_at_month = UNSET
        else:
            due_at_month = self.due_at_month

        skip_rule: Union[None, Unset, str]
        if isinstance(self.skip_rule, Unset):
            skip_rule = UNSET
        else:
            skip_rule = self.skip_rule

        repeats_strategy: Union[None, Unset, str]
        if isinstance(self.repeats_strategy, Unset):
            repeats_strategy = UNSET
        elif isinstance(self.repeats_strategy, HabitRepeatsStrategy):
            repeats_strategy = self.repeats_strategy.value
        else:
            repeats_strategy = self.repeats_strategy

        repeats_in_period_count: Union[None, Unset, int]
        if isinstance(self.repeats_in_period_count, Unset):
            repeats_in_period_count = UNSET
        else:
            repeats_in_period_count = self.repeats_in_period_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "period": period,
                "eisen": eisen,
                "difficulty": difficulty,
            }
        )
        if project_ref_id is not UNSET:
            field_dict["project_ref_id"] = project_ref_id
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
        if repeats_strategy is not UNSET:
            field_dict["repeats_strategy"] = repeats_strategy
        if repeats_in_period_count is not UNSET:
            field_dict["repeats_in_period_count"] = repeats_in_period_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        period = RecurringTaskPeriod(d.pop("period"))

        eisen = Eisen(d.pop("eisen"))

        difficulty = Difficulty(d.pop("difficulty"))

        def _parse_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_ref_id = _parse_project_ref_id(d.pop("project_ref_id", UNSET))

        def _parse_actionable_from_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        actionable_from_day = _parse_actionable_from_day(d.pop("actionable_from_day", UNSET))

        def _parse_actionable_from_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        actionable_from_month = _parse_actionable_from_month(d.pop("actionable_from_month", UNSET))

        def _parse_due_at_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        due_at_day = _parse_due_at_day(d.pop("due_at_day", UNSET))

        def _parse_due_at_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        due_at_month = _parse_due_at_month(d.pop("due_at_month", UNSET))

        def _parse_skip_rule(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        skip_rule = _parse_skip_rule(d.pop("skip_rule", UNSET))

        def _parse_repeats_strategy(data: object) -> Union[HabitRepeatsStrategy, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repeats_strategy_type_0 = HabitRepeatsStrategy(data)

                return repeats_strategy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[HabitRepeatsStrategy, None, Unset], data)

        repeats_strategy = _parse_repeats_strategy(d.pop("repeats_strategy", UNSET))

        def _parse_repeats_in_period_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        repeats_in_period_count = _parse_repeats_in_period_count(d.pop("repeats_in_period_count", UNSET))

        habit_create_args = cls(
            name=name,
            period=period,
            eisen=eisen,
            difficulty=difficulty,
            project_ref_id=project_ref_id,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            repeats_strategy=repeats_strategy,
            repeats_in_period_count=repeats_in_period_count,
        )

        habit_create_args.additional_properties = d
        return habit_create_args

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
