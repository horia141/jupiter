from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_feasability import TimePlanActivityFeasability
from ..models.time_plan_activity_kind import TimePlanActivityKind
from ..models.time_plan_activity_target import TimePlanActivityTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimePlanActivity")


@_attrs_define
class TimePlanActivity:
    """A certain activity that happens in a plan.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        time_plan_ref_id (str):
        target (TimePlanActivityTarget): The target of an activity.
        target_ref_id (str): A generic entity id.
        kind (TimePlanActivityKind): The kind of a time plan activity.
        feasability (TimePlanActivityFeasability): The feasability of a particular activity within a plan.
        archived_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    time_plan_ref_id: str
    target: TimePlanActivityTarget
    target_ref_id: str
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        time_plan_ref_id = self.time_plan_ref_id

        target = self.target.value

        target_ref_id = self.target_ref_id

        kind = self.kind.value

        feasability = self.feasability.value

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

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
                "time_plan_ref_id": time_plan_ref_id,
                "target": target,
                "target_ref_id": target_ref_id,
                "kind": kind,
                "feasability": feasability,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

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

        time_plan_ref_id = d.pop("time_plan_ref_id")

        target = TimePlanActivityTarget(d.pop("target"))

        target_ref_id = d.pop("target_ref_id")

        kind = TimePlanActivityKind(d.pop("kind"))

        feasability = TimePlanActivityFeasability(d.pop("feasability"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        time_plan_activity = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            time_plan_ref_id=time_plan_ref_id,
            target=target,
            target_ref_id=target_ref_id,
            kind=kind,
            feasability=feasability,
            archived_time=archived_time,
        )

        time_plan_activity.additional_properties = d
        return time_plan_activity

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
