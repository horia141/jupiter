from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.habit_update_args_actionable_from_day import HabitUpdateArgsActionableFromDay
    from ..models.habit_update_args_actionable_from_month import HabitUpdateArgsActionableFromMonth
    from ..models.habit_update_args_difficulty import HabitUpdateArgsDifficulty
    from ..models.habit_update_args_due_at_day import HabitUpdateArgsDueAtDay
    from ..models.habit_update_args_due_at_month import HabitUpdateArgsDueAtMonth
    from ..models.habit_update_args_eisen import HabitUpdateArgsEisen
    from ..models.habit_update_args_name import HabitUpdateArgsName
    from ..models.habit_update_args_period import HabitUpdateArgsPeriod
    from ..models.habit_update_args_project_ref_id import HabitUpdateArgsProjectRefId
    from ..models.habit_update_args_repeats_in_period_count import HabitUpdateArgsRepeatsInPeriodCount
    from ..models.habit_update_args_repeats_strategy import HabitUpdateArgsRepeatsStrategy
    from ..models.habit_update_args_skip_rule import HabitUpdateArgsSkipRule


T = TypeVar("T", bound="HabitUpdateArgs")


@_attrs_define
class HabitUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (HabitUpdateArgsName):
        project_ref_id (HabitUpdateArgsProjectRefId):
        period (HabitUpdateArgsPeriod):
        eisen (HabitUpdateArgsEisen):
        difficulty (HabitUpdateArgsDifficulty):
        actionable_from_day (HabitUpdateArgsActionableFromDay):
        actionable_from_month (HabitUpdateArgsActionableFromMonth):
        due_at_day (HabitUpdateArgsDueAtDay):
        due_at_month (HabitUpdateArgsDueAtMonth):
        skip_rule (HabitUpdateArgsSkipRule):
        repeats_strategy (HabitUpdateArgsRepeatsStrategy):
        repeats_in_period_count (HabitUpdateArgsRepeatsInPeriodCount):
    """

    ref_id: str
    name: "HabitUpdateArgsName"
    project_ref_id: "HabitUpdateArgsProjectRefId"
    period: "HabitUpdateArgsPeriod"
    eisen: "HabitUpdateArgsEisen"
    difficulty: "HabitUpdateArgsDifficulty"
    actionable_from_day: "HabitUpdateArgsActionableFromDay"
    actionable_from_month: "HabitUpdateArgsActionableFromMonth"
    due_at_day: "HabitUpdateArgsDueAtDay"
    due_at_month: "HabitUpdateArgsDueAtMonth"
    skip_rule: "HabitUpdateArgsSkipRule"
    repeats_strategy: "HabitUpdateArgsRepeatsStrategy"
    repeats_in_period_count: "HabitUpdateArgsRepeatsInPeriodCount"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        project_ref_id = self.project_ref_id.to_dict()

        period = self.period.to_dict()

        eisen = self.eisen.to_dict()

        difficulty = self.difficulty.to_dict()

        actionable_from_day = self.actionable_from_day.to_dict()

        actionable_from_month = self.actionable_from_month.to_dict()

        due_at_day = self.due_at_day.to_dict()

        due_at_month = self.due_at_month.to_dict()

        skip_rule = self.skip_rule.to_dict()

        repeats_strategy = self.repeats_strategy.to_dict()

        repeats_in_period_count = self.repeats_in_period_count.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "project_ref_id": project_ref_id,
                "period": period,
                "eisen": eisen,
                "difficulty": difficulty,
                "actionable_from_day": actionable_from_day,
                "actionable_from_month": actionable_from_month,
                "due_at_day": due_at_day,
                "due_at_month": due_at_month,
                "skip_rule": skip_rule,
                "repeats_strategy": repeats_strategy,
                "repeats_in_period_count": repeats_in_period_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.habit_update_args_actionable_from_day import HabitUpdateArgsActionableFromDay
        from ..models.habit_update_args_actionable_from_month import HabitUpdateArgsActionableFromMonth
        from ..models.habit_update_args_difficulty import HabitUpdateArgsDifficulty
        from ..models.habit_update_args_due_at_day import HabitUpdateArgsDueAtDay
        from ..models.habit_update_args_due_at_month import HabitUpdateArgsDueAtMonth
        from ..models.habit_update_args_eisen import HabitUpdateArgsEisen
        from ..models.habit_update_args_name import HabitUpdateArgsName
        from ..models.habit_update_args_period import HabitUpdateArgsPeriod
        from ..models.habit_update_args_project_ref_id import HabitUpdateArgsProjectRefId
        from ..models.habit_update_args_repeats_in_period_count import HabitUpdateArgsRepeatsInPeriodCount
        from ..models.habit_update_args_repeats_strategy import HabitUpdateArgsRepeatsStrategy
        from ..models.habit_update_args_skip_rule import HabitUpdateArgsSkipRule

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = HabitUpdateArgsName.from_dict(d.pop("name"))

        project_ref_id = HabitUpdateArgsProjectRefId.from_dict(d.pop("project_ref_id"))

        period = HabitUpdateArgsPeriod.from_dict(d.pop("period"))

        eisen = HabitUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = HabitUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_from_day = HabitUpdateArgsActionableFromDay.from_dict(d.pop("actionable_from_day"))

        actionable_from_month = HabitUpdateArgsActionableFromMonth.from_dict(d.pop("actionable_from_month"))

        due_at_day = HabitUpdateArgsDueAtDay.from_dict(d.pop("due_at_day"))

        due_at_month = HabitUpdateArgsDueAtMonth.from_dict(d.pop("due_at_month"))

        skip_rule = HabitUpdateArgsSkipRule.from_dict(d.pop("skip_rule"))

        repeats_strategy = HabitUpdateArgsRepeatsStrategy.from_dict(d.pop("repeats_strategy"))

        repeats_in_period_count = HabitUpdateArgsRepeatsInPeriodCount.from_dict(d.pop("repeats_in_period_count"))

        habit_update_args = cls(
            ref_id=ref_id,
            name=name,
            project_ref_id=project_ref_id,
            period=period,
            eisen=eisen,
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            skip_rule=skip_rule,
            repeats_strategy=repeats_strategy,
            repeats_in_period_count=repeats_in_period_count,
        )

        habit_update_args.additional_properties = d
        return habit_update_args

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
