from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSummariesArgs")


@_attrs_define
class GetSummariesArgs:
    """Get summaries args.

    Attributes:
        allow_archived (Union[None, Unset, bool]):
        include_workspace (Union[None, Unset, bool]):
        include_schedule_streams (Union[None, Unset, bool]):
        include_vacations (Union[None, Unset, bool]):
        include_projects (Union[None, Unset, bool]):
        include_inbox_tasks (Union[None, Unset, bool]):
        include_journals_last_year (Union[None, Unset, bool]):
        include_habits (Union[None, Unset, bool]):
        include_chores (Union[None, Unset, bool]):
        include_big_plans (Union[None, Unset, bool]):
        include_smart_lists (Union[None, Unset, bool]):
        include_metrics (Union[None, Unset, bool]):
        include_persons (Union[None, Unset, bool]):
    """

    allow_archived: Union[None, Unset, bool] = UNSET
    include_workspace: Union[None, Unset, bool] = UNSET
    include_schedule_streams: Union[None, Unset, bool] = UNSET
    include_vacations: Union[None, Unset, bool] = UNSET
    include_projects: Union[None, Unset, bool] = UNSET
    include_inbox_tasks: Union[None, Unset, bool] = UNSET
    include_journals_last_year: Union[None, Unset, bool] = UNSET
    include_habits: Union[None, Unset, bool] = UNSET
    include_chores: Union[None, Unset, bool] = UNSET
    include_big_plans: Union[None, Unset, bool] = UNSET
    include_smart_lists: Union[None, Unset, bool] = UNSET
    include_metrics: Union[None, Unset, bool] = UNSET
    include_persons: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_archived: Union[None, Unset, bool]
        if isinstance(self.allow_archived, Unset):
            allow_archived = UNSET
        else:
            allow_archived = self.allow_archived

        include_workspace: Union[None, Unset, bool]
        if isinstance(self.include_workspace, Unset):
            include_workspace = UNSET
        else:
            include_workspace = self.include_workspace

        include_schedule_streams: Union[None, Unset, bool]
        if isinstance(self.include_schedule_streams, Unset):
            include_schedule_streams = UNSET
        else:
            include_schedule_streams = self.include_schedule_streams

        include_vacations: Union[None, Unset, bool]
        if isinstance(self.include_vacations, Unset):
            include_vacations = UNSET
        else:
            include_vacations = self.include_vacations

        include_projects: Union[None, Unset, bool]
        if isinstance(self.include_projects, Unset):
            include_projects = UNSET
        else:
            include_projects = self.include_projects

        include_inbox_tasks: Union[None, Unset, bool]
        if isinstance(self.include_inbox_tasks, Unset):
            include_inbox_tasks = UNSET
        else:
            include_inbox_tasks = self.include_inbox_tasks

        include_journals_last_year: Union[None, Unset, bool]
        if isinstance(self.include_journals_last_year, Unset):
            include_journals_last_year = UNSET
        else:
            include_journals_last_year = self.include_journals_last_year

        include_habits: Union[None, Unset, bool]
        if isinstance(self.include_habits, Unset):
            include_habits = UNSET
        else:
            include_habits = self.include_habits

        include_chores: Union[None, Unset, bool]
        if isinstance(self.include_chores, Unset):
            include_chores = UNSET
        else:
            include_chores = self.include_chores

        include_big_plans: Union[None, Unset, bool]
        if isinstance(self.include_big_plans, Unset):
            include_big_plans = UNSET
        else:
            include_big_plans = self.include_big_plans

        include_smart_lists: Union[None, Unset, bool]
        if isinstance(self.include_smart_lists, Unset):
            include_smart_lists = UNSET
        else:
            include_smart_lists = self.include_smart_lists

        include_metrics: Union[None, Unset, bool]
        if isinstance(self.include_metrics, Unset):
            include_metrics = UNSET
        else:
            include_metrics = self.include_metrics

        include_persons: Union[None, Unset, bool]
        if isinstance(self.include_persons, Unset):
            include_persons = UNSET
        else:
            include_persons = self.include_persons

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_archived is not UNSET:
            field_dict["allow_archived"] = allow_archived
        if include_workspace is not UNSET:
            field_dict["include_workspace"] = include_workspace
        if include_schedule_streams is not UNSET:
            field_dict["include_schedule_streams"] = include_schedule_streams
        if include_vacations is not UNSET:
            field_dict["include_vacations"] = include_vacations
        if include_projects is not UNSET:
            field_dict["include_projects"] = include_projects
        if include_inbox_tasks is not UNSET:
            field_dict["include_inbox_tasks"] = include_inbox_tasks
        if include_journals_last_year is not UNSET:
            field_dict["include_journals_last_year"] = include_journals_last_year
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_allow_archived(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        allow_archived = _parse_allow_archived(d.pop("allow_archived", UNSET))

        def _parse_include_workspace(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_workspace = _parse_include_workspace(d.pop("include_workspace", UNSET))

        def _parse_include_schedule_streams(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_schedule_streams = _parse_include_schedule_streams(d.pop("include_schedule_streams", UNSET))

        def _parse_include_vacations(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_vacations = _parse_include_vacations(d.pop("include_vacations", UNSET))

        def _parse_include_projects(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_projects = _parse_include_projects(d.pop("include_projects", UNSET))

        def _parse_include_inbox_tasks(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_inbox_tasks = _parse_include_inbox_tasks(d.pop("include_inbox_tasks", UNSET))

        def _parse_include_journals_last_year(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_journals_last_year = _parse_include_journals_last_year(d.pop("include_journals_last_year", UNSET))

        def _parse_include_habits(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_habits = _parse_include_habits(d.pop("include_habits", UNSET))

        def _parse_include_chores(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_chores = _parse_include_chores(d.pop("include_chores", UNSET))

        def _parse_include_big_plans(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_big_plans = _parse_include_big_plans(d.pop("include_big_plans", UNSET))

        def _parse_include_smart_lists(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_smart_lists = _parse_include_smart_lists(d.pop("include_smart_lists", UNSET))

        def _parse_include_metrics(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_metrics = _parse_include_metrics(d.pop("include_metrics", UNSET))

        def _parse_include_persons(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_persons = _parse_include_persons(d.pop("include_persons", UNSET))

        get_summaries_args = cls(
            allow_archived=allow_archived,
            include_workspace=include_workspace,
            include_schedule_streams=include_schedule_streams,
            include_vacations=include_vacations,
            include_projects=include_projects,
            include_inbox_tasks=include_inbox_tasks,
            include_journals_last_year=include_journals_last_year,
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
