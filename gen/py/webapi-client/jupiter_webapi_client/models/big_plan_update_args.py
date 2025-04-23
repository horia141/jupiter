from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.big_plan_update_args_actionable_date import BigPlanUpdateArgsActionableDate
    from ..models.big_plan_update_args_difficulty import BigPlanUpdateArgsDifficulty
    from ..models.big_plan_update_args_due_date import BigPlanUpdateArgsDueDate
    from ..models.big_plan_update_args_eisen import BigPlanUpdateArgsEisen
    from ..models.big_plan_update_args_name import BigPlanUpdateArgsName
    from ..models.big_plan_update_args_project_ref_id import BigPlanUpdateArgsProjectRefId
    from ..models.big_plan_update_args_status import BigPlanUpdateArgsStatus


T = TypeVar("T", bound="BigPlanUpdateArgs")


@_attrs_define
class BigPlanUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (BigPlanUpdateArgsName):
        status (BigPlanUpdateArgsStatus):
        project_ref_id (BigPlanUpdateArgsProjectRefId):
        eisen (BigPlanUpdateArgsEisen):
        difficulty (BigPlanUpdateArgsDifficulty):
        actionable_date (BigPlanUpdateArgsActionableDate):
        due_date (BigPlanUpdateArgsDueDate):
    """

    ref_id: str
    name: "BigPlanUpdateArgsName"
    status: "BigPlanUpdateArgsStatus"
    project_ref_id: "BigPlanUpdateArgsProjectRefId"
    eisen: "BigPlanUpdateArgsEisen"
    difficulty: "BigPlanUpdateArgsDifficulty"
    actionable_date: "BigPlanUpdateArgsActionableDate"
    due_date: "BigPlanUpdateArgsDueDate"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        status = self.status.to_dict()

        project_ref_id = self.project_ref_id.to_dict()

        eisen = self.eisen.to_dict()

        difficulty = self.difficulty.to_dict()

        actionable_date = self.actionable_date.to_dict()

        due_date = self.due_date.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "status": status,
                "project_ref_id": project_ref_id,
                "eisen": eisen,
                "difficulty": difficulty,
                "actionable_date": actionable_date,
                "due_date": due_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan_update_args_actionable_date import BigPlanUpdateArgsActionableDate
        from ..models.big_plan_update_args_difficulty import BigPlanUpdateArgsDifficulty
        from ..models.big_plan_update_args_due_date import BigPlanUpdateArgsDueDate
        from ..models.big_plan_update_args_eisen import BigPlanUpdateArgsEisen
        from ..models.big_plan_update_args_name import BigPlanUpdateArgsName
        from ..models.big_plan_update_args_project_ref_id import BigPlanUpdateArgsProjectRefId
        from ..models.big_plan_update_args_status import BigPlanUpdateArgsStatus

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = BigPlanUpdateArgsName.from_dict(d.pop("name"))

        status = BigPlanUpdateArgsStatus.from_dict(d.pop("status"))

        project_ref_id = BigPlanUpdateArgsProjectRefId.from_dict(d.pop("project_ref_id"))

        eisen = BigPlanUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = BigPlanUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_date = BigPlanUpdateArgsActionableDate.from_dict(d.pop("actionable_date"))

        due_date = BigPlanUpdateArgsDueDate.from_dict(d.pop("due_date"))

        big_plan_update_args = cls(
            ref_id=ref_id,
            name=name,
            status=status,
            project_ref_id=project_ref_id,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
        )

        big_plan_update_args.additional_properties = d
        return big_plan_update_args

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
