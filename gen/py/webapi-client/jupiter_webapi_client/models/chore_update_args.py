from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chore_update_args_actionable_from_day import ChoreUpdateArgsActionableFromDay
    from ..models.chore_update_args_actionable_from_month import ChoreUpdateArgsActionableFromMonth
    from ..models.chore_update_args_difficulty import ChoreUpdateArgsDifficulty
    from ..models.chore_update_args_due_at_day import ChoreUpdateArgsDueAtDay
    from ..models.chore_update_args_due_at_month import ChoreUpdateArgsDueAtMonth
    from ..models.chore_update_args_eisen import ChoreUpdateArgsEisen
    from ..models.chore_update_args_end_at_date import ChoreUpdateArgsEndAtDate
    from ..models.chore_update_args_must_do import ChoreUpdateArgsMustDo
    from ..models.chore_update_args_name import ChoreUpdateArgsName
    from ..models.chore_update_args_period import ChoreUpdateArgsPeriod
    from ..models.chore_update_args_project_ref_id import ChoreUpdateArgsProjectRefId
    from ..models.chore_update_args_skip_rule import ChoreUpdateArgsSkipRule
    from ..models.chore_update_args_start_at_date import ChoreUpdateArgsStartAtDate


T = TypeVar("T", bound="ChoreUpdateArgs")


@_attrs_define
class ChoreUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (ChoreUpdateArgsName):
        project_ref_id (ChoreUpdateArgsProjectRefId):
        period (ChoreUpdateArgsPeriod):
        eisen (ChoreUpdateArgsEisen):
        difficulty (ChoreUpdateArgsDifficulty):
        actionable_from_day (ChoreUpdateArgsActionableFromDay):
        actionable_from_month (ChoreUpdateArgsActionableFromMonth):
        due_at_day (ChoreUpdateArgsDueAtDay):
        due_at_month (ChoreUpdateArgsDueAtMonth):
        must_do (ChoreUpdateArgsMustDo):
        skip_rule (ChoreUpdateArgsSkipRule):
        start_at_date (ChoreUpdateArgsStartAtDate):
        end_at_date (ChoreUpdateArgsEndAtDate):
    """

    ref_id: str
    name: "ChoreUpdateArgsName"
    project_ref_id: "ChoreUpdateArgsProjectRefId"
    period: "ChoreUpdateArgsPeriod"
    eisen: "ChoreUpdateArgsEisen"
    difficulty: "ChoreUpdateArgsDifficulty"
    actionable_from_day: "ChoreUpdateArgsActionableFromDay"
    actionable_from_month: "ChoreUpdateArgsActionableFromMonth"
    due_at_day: "ChoreUpdateArgsDueAtDay"
    due_at_month: "ChoreUpdateArgsDueAtMonth"
    must_do: "ChoreUpdateArgsMustDo"
    skip_rule: "ChoreUpdateArgsSkipRule"
    start_at_date: "ChoreUpdateArgsStartAtDate"
    end_at_date: "ChoreUpdateArgsEndAtDate"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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

        must_do = self.must_do.to_dict()

        skip_rule = self.skip_rule.to_dict()

        start_at_date = self.start_at_date.to_dict()

        end_at_date = self.end_at_date.to_dict()

        field_dict: Dict[str, Any] = {}
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
                "must_do": must_do,
                "skip_rule": skip_rule,
                "start_at_date": start_at_date,
                "end_at_date": end_at_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chore_update_args_actionable_from_day import ChoreUpdateArgsActionableFromDay
        from ..models.chore_update_args_actionable_from_month import ChoreUpdateArgsActionableFromMonth
        from ..models.chore_update_args_difficulty import ChoreUpdateArgsDifficulty
        from ..models.chore_update_args_due_at_day import ChoreUpdateArgsDueAtDay
        from ..models.chore_update_args_due_at_month import ChoreUpdateArgsDueAtMonth
        from ..models.chore_update_args_eisen import ChoreUpdateArgsEisen
        from ..models.chore_update_args_end_at_date import ChoreUpdateArgsEndAtDate
        from ..models.chore_update_args_must_do import ChoreUpdateArgsMustDo
        from ..models.chore_update_args_name import ChoreUpdateArgsName
        from ..models.chore_update_args_period import ChoreUpdateArgsPeriod
        from ..models.chore_update_args_project_ref_id import ChoreUpdateArgsProjectRefId
        from ..models.chore_update_args_skip_rule import ChoreUpdateArgsSkipRule
        from ..models.chore_update_args_start_at_date import ChoreUpdateArgsStartAtDate

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = ChoreUpdateArgsName.from_dict(d.pop("name"))

        project_ref_id = ChoreUpdateArgsProjectRefId.from_dict(d.pop("project_ref_id"))

        period = ChoreUpdateArgsPeriod.from_dict(d.pop("period"))

        eisen = ChoreUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = ChoreUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_from_day = ChoreUpdateArgsActionableFromDay.from_dict(d.pop("actionable_from_day"))

        actionable_from_month = ChoreUpdateArgsActionableFromMonth.from_dict(d.pop("actionable_from_month"))

        due_at_day = ChoreUpdateArgsDueAtDay.from_dict(d.pop("due_at_day"))

        due_at_month = ChoreUpdateArgsDueAtMonth.from_dict(d.pop("due_at_month"))

        must_do = ChoreUpdateArgsMustDo.from_dict(d.pop("must_do"))

        skip_rule = ChoreUpdateArgsSkipRule.from_dict(d.pop("skip_rule"))

        start_at_date = ChoreUpdateArgsStartAtDate.from_dict(d.pop("start_at_date"))

        end_at_date = ChoreUpdateArgsEndAtDate.from_dict(d.pop("end_at_date"))

        chore_update_args = cls(
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
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date,
            end_at_date=end_at_date,
        )

        chore_update_args.additional_properties = d
        return chore_update_args

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
