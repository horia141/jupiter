from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSummariesArgs")


@_attrs_define
class GetSummariesArgs:
    """Get summaries args.

    Attributes:
        allow_archived (Union[Unset, bool]):
        include_vacations (Union[Unset, bool]):
        include_projects (Union[Unset, bool]):
        include_inbox_tasks (Union[Unset, bool]):
        include_habits (Union[Unset, bool]):
        include_chores (Union[Unset, bool]):
        include_big_plans (Union[Unset, bool]):
        include_smart_lists (Union[Unset, bool]):
        include_metrics (Union[Unset, bool]):
        include_persons (Union[Unset, bool]):
    """

    allow_archived: Union[Unset, bool] = UNSET
    include_vacations: Union[Unset, bool] = UNSET
    include_projects: Union[Unset, bool] = UNSET
    include_inbox_tasks: Union[Unset, bool] = UNSET
    include_habits: Union[Unset, bool] = UNSET
    include_chores: Union[Unset, bool] = UNSET
    include_big_plans: Union[Unset, bool] = UNSET
    include_smart_lists: Union[Unset, bool] = UNSET
    include_metrics: Union[Unset, bool] = UNSET
    include_persons: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        include_vacations = self.include_vacations

        include_projects = self.include_projects

        include_inbox_tasks = self.include_inbox_tasks

        include_habits = self.include_habits

        include_chores = self.include_chores

        include_big_plans = self.include_big_plans

        include_smart_lists = self.include_smart_lists

        include_metrics = self.include_metrics

        include_persons = self.include_persons

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_archived is not UNSET:
            field_dict["allow_archived"] = allow_archived
        if include_vacations is not UNSET:
            field_dict["include_vacations"] = include_vacations
        if include_projects is not UNSET:
            field_dict["include_projects"] = include_projects
        if include_inbox_tasks is not UNSET:
            field_dict["include_inbox_tasks"] = include_inbox_tasks
        if include_habits is not UNSET:
            field_dict["include_habits"] = include_habits
        if include_chores is not UNSET:
            field_dict["include_chores"] = include_chores
        if include_big_plans is not UNSET:
            field_dict["include_big_plans"] = include_big_plans
        if include_smart_lists is not UNSET:
            field_dict["include_smart_lists"] = include_smart_lists
        if include_metrics is not UNSET:
            field_dict["include_metrics"] = include_metrics
        if include_persons is not UNSET:
            field_dict["include_persons"] = include_persons

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived", UNSET)

        include_vacations = d.pop("include_vacations", UNSET)

        include_projects = d.pop("include_projects", UNSET)

        include_inbox_tasks = d.pop("include_inbox_tasks", UNSET)

        include_habits = d.pop("include_habits", UNSET)

        include_chores = d.pop("include_chores", UNSET)

        include_big_plans = d.pop("include_big_plans", UNSET)

        include_smart_lists = d.pop("include_smart_lists", UNSET)

        include_metrics = d.pop("include_metrics", UNSET)

        include_persons = d.pop("include_persons", UNSET)

        get_summaries_args = cls(
            allow_archived=allow_archived,
            include_vacations=include_vacations,
            include_projects=include_projects,
            include_inbox_tasks=include_inbox_tasks,
            include_habits=include_habits,
            include_chores=include_chores,
            include_big_plans=include_big_plans,
            include_smart_lists=include_smart_lists,
            include_metrics=include_metrics,
            include_persons=include_persons,
        )

        get_summaries_args.additional_properties = d
        return get_summaries_args

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
