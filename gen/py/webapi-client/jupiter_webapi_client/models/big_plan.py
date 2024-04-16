from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.big_plan_status import BigPlanStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="BigPlan")


@_attrs_define
class BigPlan:
    """A big plan.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The big plan name.
        big_plan_collection (str):
        project_ref_id (str): A generic entity id.
        status (BigPlanStatus): The status of a big plan.
        archived_time (Union[Unset, str]): A timestamp in the application.
        actionable_date (Union[Unset, str]): A date or possibly a datetime for the application.
        due_date (Union[Unset, str]): A date or possibly a datetime for the application.
        accepted_time (Union[Unset, str]): A timestamp in the application.
        working_time (Union[Unset, str]): A timestamp in the application.
        completed_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    big_plan_collection: str
    project_ref_id: str
    status: BigPlanStatus
    archived_time: Union[Unset, str] = UNSET
    actionable_date: Union[Unset, str] = UNSET
    due_date: Union[Unset, str] = UNSET
    accepted_time: Union[Unset, str] = UNSET
    working_time: Union[Unset, str] = UNSET
    completed_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        big_plan_collection = self.big_plan_collection

        project_ref_id = self.project_ref_id

        status = self.status.value

        archived_time = self.archived_time

        actionable_date = self.actionable_date

        due_date = self.due_date

        accepted_time = self.accepted_time

        working_time = self.working_time

        completed_time = self.completed_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "big_plan_collection": big_plan_collection,
                "project_ref_id": project_ref_id,
                "status": status,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date
        if due_date is not UNSET:
            field_dict["due_date"] = due_date
        if accepted_time is not UNSET:
            field_dict["accepted_time"] = accepted_time
        if working_time is not UNSET:
            field_dict["working_time"] = working_time
        if completed_time is not UNSET:
            field_dict["completed_time"] = completed_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        big_plan_collection = d.pop("big_plan_collection")

        project_ref_id = d.pop("project_ref_id")

        status = BigPlanStatus(d.pop("status"))

        archived_time = d.pop("archived_time", UNSET)

        actionable_date = d.pop("actionable_date", UNSET)

        due_date = d.pop("due_date", UNSET)

        accepted_time = d.pop("accepted_time", UNSET)

        working_time = d.pop("working_time", UNSET)

        completed_time = d.pop("completed_time", UNSET)

        big_plan = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            big_plan_collection=big_plan_collection,
            project_ref_id=project_ref_id,
            status=status,
            archived_time=archived_time,
            actionable_date=actionable_date,
            due_date=due_date,
            accepted_time=accepted_time,
            working_time=working_time,
            completed_time=completed_time,
        )

        big_plan.additional_properties = d
        return big_plan

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
