from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TimePlanAssociateWithInboxTasksArgs")


@_attrs_define
class TimePlanAssociateWithInboxTasksArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        inbox_task_ref_ids (List[str]):
        override_existing_dates (bool):
    """

    ref_id: str
    inbox_task_ref_ids: List[str]
    override_existing_dates: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        inbox_task_ref_ids = self.inbox_task_ref_ids

        override_existing_dates = self.override_existing_dates

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "inbox_task_ref_ids": inbox_task_ref_ids,
                "override_existing_dates": override_existing_dates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        inbox_task_ref_ids = cast(List[str], d.pop("inbox_task_ref_ids"))

        override_existing_dates = d.pop("override_existing_dates")

        time_plan_associate_with_inbox_tasks_args = cls(
            ref_id=ref_id,
            inbox_task_ref_ids=inbox_task_ref_ids,
            override_existing_dates=override_existing_dates,
        )

        time_plan_associate_with_inbox_tasks_args.additional_properties = d
        return time_plan_associate_with_inbox_tasks_args

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
