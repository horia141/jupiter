from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_feasability import TimePlanActivityFeasability
from ..models.time_plan_activity_kind import TimePlanActivityKind

T = TypeVar("T", bound="TimePlanAssociateWithInboxTasksArgs")


@_attrs_define
class TimePlanAssociateWithInboxTasksArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        inbox_task_ref_ids (list[str]):
        override_existing_dates (bool):
        kind (TimePlanActivityKind): The kind of a time plan activity.
        feasability (TimePlanActivityFeasability): The feasability of a particular activity within a plan.
    """

    ref_id: str
    inbox_task_ref_ids: list[str]
    override_existing_dates: bool
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        inbox_task_ref_ids = self.inbox_task_ref_ids

        override_existing_dates = self.override_existing_dates

        kind = self.kind.value

        feasability = self.feasability.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "inbox_task_ref_ids": inbox_task_ref_ids,
                "override_existing_dates": override_existing_dates,
                "kind": kind,
                "feasability": feasability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        inbox_task_ref_ids = cast(list[str], d.pop("inbox_task_ref_ids"))

        override_existing_dates = d.pop("override_existing_dates")

        kind = TimePlanActivityKind(d.pop("kind"))

        feasability = TimePlanActivityFeasability(d.pop("feasability"))

        time_plan_associate_with_inbox_tasks_args = cls(
            ref_id=ref_id,
            inbox_task_ref_ids=inbox_task_ref_ids,
            override_existing_dates=override_existing_dates,
            kind=kind,
            feasability=feasability,
        )

        time_plan_associate_with_inbox_tasks_args.additional_properties = d
        return time_plan_associate_with_inbox_tasks_args

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
