from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

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
        big_plan_collection_ref_id (str):
        project_ref_id (str): A generic entity id.
        status (BigPlanStatus): The status of a big plan.
        archived_time (Union[None, Unset, str]):
        actionable_date (Union[None, Unset, str]):
        due_date (Union[None, Unset, str]):
        working_time (Union[None, Unset, str]):
        completed_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    big_plan_collection_ref_id: str
    project_ref_id: str
    status: BigPlanStatus
    archived_time: Union[None, Unset, str] = UNSET
    actionable_date: Union[None, Unset, str] = UNSET
    due_date: Union[None, Unset, str] = UNSET
    working_time: Union[None, Unset, str] = UNSET
    completed_time: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        big_plan_collection_ref_id = self.big_plan_collection_ref_id

        project_ref_id = self.project_ref_id

        status = self.status.value

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        actionable_date: Union[None, Unset, str]
        if isinstance(self.actionable_date, Unset):
            actionable_date = UNSET
        else:
            actionable_date = self.actionable_date

        due_date: Union[None, Unset, str]
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        working_time: Union[None, Unset, str]
        if isinstance(self.working_time, Unset):
            working_time = UNSET
        else:
            working_time = self.working_time

        completed_time: Union[None, Unset, str]
        if isinstance(self.completed_time, Unset):
            completed_time = UNSET
        else:
            completed_time = self.completed_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "big_plan_collection_ref_id": big_plan_collection_ref_id,
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
        if working_time is not UNSET:
            field_dict["working_time"] = working_time
        if completed_time is not UNSET:
            field_dict["completed_time"] = completed_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        big_plan_collection_ref_id = d.pop("big_plan_collection_ref_id")

        project_ref_id = d.pop("project_ref_id")

        status = BigPlanStatus(d.pop("status"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_actionable_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        actionable_date = _parse_actionable_date(d.pop("actionable_date", UNSET))

        def _parse_due_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        def _parse_working_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        working_time = _parse_working_time(d.pop("working_time", UNSET))

        def _parse_completed_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        completed_time = _parse_completed_time(d.pop("completed_time", UNSET))

        big_plan = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            big_plan_collection_ref_id=big_plan_collection_ref_id,
            project_ref_id=project_ref_id,
            status=status,
            archived_time=archived_time,
            actionable_date=actionable_date,
            due_date=due_date,
            working_time=working_time,
            completed_time=completed_time,
        )

        big_plan.additional_properties = d
        return big_plan

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
