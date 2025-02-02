from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_feasability import TimePlanActivityFeasability
from ..models.time_plan_activity_kind import TimePlanActivityKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="BigPlanCreateArgs")


@_attrs_define
class BigPlanCreateArgs:
    """Big plan create args.

    Attributes:
        name (str): The big plan name.
        time_plan_ref_id (Union[None, Unset, str]):
        time_plan_activity_kind (Union[None, TimePlanActivityKind, Unset]):
        time_plan_activity_feasability (Union[None, TimePlanActivityFeasability, Unset]):
        project_ref_id (Union[None, Unset, str]):
        actionable_date (Union[None, Unset, str]):
        due_date (Union[None, Unset, str]):
    """

    name: str
    time_plan_ref_id: Union[None, Unset, str] = UNSET
    time_plan_activity_kind: Union[None, TimePlanActivityKind, Unset] = UNSET
    time_plan_activity_feasability: Union[None, TimePlanActivityFeasability, Unset] = UNSET
    project_ref_id: Union[None, Unset, str] = UNSET
    actionable_date: Union[None, Unset, str] = UNSET
    due_date: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        time_plan_ref_id: Union[None, Unset, str]
        if isinstance(self.time_plan_ref_id, Unset):
            time_plan_ref_id = UNSET
        else:
            time_plan_ref_id = self.time_plan_ref_id

        time_plan_activity_kind: Union[None, Unset, str]
        if isinstance(self.time_plan_activity_kind, Unset):
            time_plan_activity_kind = UNSET
        elif isinstance(self.time_plan_activity_kind, TimePlanActivityKind):
            time_plan_activity_kind = self.time_plan_activity_kind.value
        else:
            time_plan_activity_kind = self.time_plan_activity_kind

        time_plan_activity_feasability: Union[None, Unset, str]
        if isinstance(self.time_plan_activity_feasability, Unset):
            time_plan_activity_feasability = UNSET
        elif isinstance(self.time_plan_activity_feasability, TimePlanActivityFeasability):
            time_plan_activity_feasability = self.time_plan_activity_feasability.value
        else:
            time_plan_activity_feasability = self.time_plan_activity_feasability

        project_ref_id: Union[None, Unset, str]
        if isinstance(self.project_ref_id, Unset):
            project_ref_id = UNSET
        else:
            project_ref_id = self.project_ref_id

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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if time_plan_ref_id is not UNSET:
            field_dict["time_plan_ref_id"] = time_plan_ref_id
        if time_plan_activity_kind is not UNSET:
            field_dict["time_plan_activity_kind"] = time_plan_activity_kind
        if time_plan_activity_feasability is not UNSET:
            field_dict["time_plan_activity_feasability"] = time_plan_activity_feasability
        if project_ref_id is not UNSET:
            field_dict["project_ref_id"] = project_ref_id
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date
        if due_date is not UNSET:
            field_dict["due_date"] = due_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        def _parse_time_plan_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        time_plan_ref_id = _parse_time_plan_ref_id(d.pop("time_plan_ref_id", UNSET))

        def _parse_time_plan_activity_kind(data: object) -> Union[None, TimePlanActivityKind, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                time_plan_activity_kind_type_0 = TimePlanActivityKind(data)

                return time_plan_activity_kind_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TimePlanActivityKind, Unset], data)

        time_plan_activity_kind = _parse_time_plan_activity_kind(d.pop("time_plan_activity_kind", UNSET))

        def _parse_time_plan_activity_feasability(data: object) -> Union[None, TimePlanActivityFeasability, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                time_plan_activity_feasability_type_0 = TimePlanActivityFeasability(data)

                return time_plan_activity_feasability_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TimePlanActivityFeasability, Unset], data)

        time_plan_activity_feasability = _parse_time_plan_activity_feasability(
            d.pop("time_plan_activity_feasability", UNSET)
        )

        def _parse_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_ref_id = _parse_project_ref_id(d.pop("project_ref_id", UNSET))

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

        big_plan_create_args = cls(
            name=name,
            time_plan_ref_id=time_plan_ref_id,
            time_plan_activity_kind=time_plan_activity_kind,
            time_plan_activity_feasability=time_plan_activity_feasability,
            project_ref_id=project_ref_id,
            actionable_date=actionable_date,
            due_date=due_date,
        )

        big_plan_create_args.additional_properties = d
        return big_plan_create_args

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
