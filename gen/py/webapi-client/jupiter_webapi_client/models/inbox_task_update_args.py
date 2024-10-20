from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task_update_args_actionable_date import InboxTaskUpdateArgsActionableDate
    from ..models.inbox_task_update_args_difficulty import InboxTaskUpdateArgsDifficulty
    from ..models.inbox_task_update_args_due_date import InboxTaskUpdateArgsDueDate
    from ..models.inbox_task_update_args_eisen import InboxTaskUpdateArgsEisen
    from ..models.inbox_task_update_args_name import InboxTaskUpdateArgsName
    from ..models.inbox_task_update_args_status import InboxTaskUpdateArgsStatus


T = TypeVar("T", bound="InboxTaskUpdateArgs")


@_attrs_define
class InboxTaskUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (InboxTaskUpdateArgsName):
        status (InboxTaskUpdateArgsStatus):
        eisen (InboxTaskUpdateArgsEisen):
        difficulty (InboxTaskUpdateArgsDifficulty):
        actionable_date (InboxTaskUpdateArgsActionableDate):
        due_date (InboxTaskUpdateArgsDueDate):
    """

    ref_id: str
    name: "InboxTaskUpdateArgsName"
    status: "InboxTaskUpdateArgsStatus"
    eisen: "InboxTaskUpdateArgsEisen"
    difficulty: "InboxTaskUpdateArgsDifficulty"
    actionable_date: "InboxTaskUpdateArgsActionableDate"
    due_date: "InboxTaskUpdateArgsDueDate"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        status = self.status.to_dict()

        eisen = self.eisen.to_dict()

        difficulty = self.difficulty.to_dict()

        actionable_date = self.actionable_date.to_dict()

        due_date = self.due_date.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "status": status,
                "eisen": eisen,
                "difficulty": difficulty,
                "actionable_date": actionable_date,
                "due_date": due_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task_update_args_actionable_date import InboxTaskUpdateArgsActionableDate
        from ..models.inbox_task_update_args_difficulty import InboxTaskUpdateArgsDifficulty
        from ..models.inbox_task_update_args_due_date import InboxTaskUpdateArgsDueDate
        from ..models.inbox_task_update_args_eisen import InboxTaskUpdateArgsEisen
        from ..models.inbox_task_update_args_name import InboxTaskUpdateArgsName
        from ..models.inbox_task_update_args_status import InboxTaskUpdateArgsStatus

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = InboxTaskUpdateArgsName.from_dict(d.pop("name"))

        status = InboxTaskUpdateArgsStatus.from_dict(d.pop("status"))

        eisen = InboxTaskUpdateArgsEisen.from_dict(d.pop("eisen"))

        difficulty = InboxTaskUpdateArgsDifficulty.from_dict(d.pop("difficulty"))

        actionable_date = InboxTaskUpdateArgsActionableDate.from_dict(d.pop("actionable_date"))

        due_date = InboxTaskUpdateArgsDueDate.from_dict(d.pop("due_date"))

        inbox_task_update_args = cls(
            ref_id=ref_id,
            name=name,
            status=status,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
        )

        inbox_task_update_args.additional_properties = d
        return inbox_task_update_args

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
