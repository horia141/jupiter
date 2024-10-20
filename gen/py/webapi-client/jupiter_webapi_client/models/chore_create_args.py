from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChoreCreateArgs")


@_attrs_define
class ChoreCreateArgs:
    """ChoreCreate args.

    Attributes:
        name (str): The chore name.
        period (RecurringTaskPeriod): A period for a particular task.
        must_do (bool):
        project_ref_id (Union[None, Unset, str]):
        eisen (Union[Eisen, None, Unset]):
        difficulty (Union[Difficulty, None, Unset]):
        actionable_from_day (Union[None, Unset, int]):
        actionable_from_month (Union[None, Unset, int]):
        due_at_day (Union[None, Unset, int]):
        due_at_month (Union[None, Unset, int]):
        skip_rule (Union[None, Unset, str]):
        start_at_date (Union[None, Unset, str]):
        end_at_date (Union[None, Unset, str]):
    """

    name: str
    period: RecurringTaskPeriod
    must_do: bool
    project_ref_id: Union[None, Unset, str] = UNSET
    eisen: Union[Eisen, None, Unset] = UNSET
    difficulty: Union[Difficulty, None, Unset] = UNSET
    actionable_from_day: Union[None, Unset, int] = UNSET
    actionable_from_month: Union[None, Unset, int] = UNSET
    due_at_day: Union[None, Unset, int] = UNSET
    due_at_month: Union[None, Unset, int] = UNSET
    skip_rule: Union[None, Unset, str] = UNSET
    start_at_date: Union[None, Unset, str] = UNSET
    end_at_date: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        period = self.period.value

        must_do = self.must_do

        project_ref_id: Union[None, Unset, str]
        if isinstance(self.project_ref_id, Unset):
            project_ref_id = UNSET
        else:
            project_ref_id = self.project_ref_id

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

        start_at_date: Union[None, Unset, str]
        if isinstance(self.start_at_date, Unset):
            start_at_date = UNSET
        else:
            start_at_date = self.start_at_date

        end_at_date: Union[None, Unset, str]
        if isinstance(self.end_at_date, Unset):
            end_at_date = UNSET
        else:
            end_at_date = self.end_at_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "period": period,
                "must_do": must_do,
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
        if start_at_date is not UNSET:
            field_dict["start_at_date"] = start_at_date
        if end_at_date is not UNSET:
            field_dict["end_at_date"] = end_at_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        period = RecurringTaskPeriod(d.pop("period"))

        must_do = d.pop("must_do")

        def _parse_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_ref_id = _parse_project_ref_id(d.pop("project_ref_id", UNSET))

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

        def _parse_start_at_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        start_at_date = _parse_start_at_date(d.pop("start_at_date", UNSET))

        def _parse_end_at_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        end_at_date = _parse_end_at_date(d.pop("end_at_date", UNSET))

        chore_create_args = cls(
            name=name,
            period=period,
            must_do=must_do,
            project_ref_id=project_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            start_at_date=start_at_date,
            end_at_date=end_at_date,
        )

        chore_create_args.additional_properties = d
        return chore_create_args

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
