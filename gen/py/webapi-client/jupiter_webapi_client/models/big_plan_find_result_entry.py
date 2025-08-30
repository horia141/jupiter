from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.big_plan_milestone import BigPlanMilestone
    from ..models.big_plan_stats import BigPlanStats
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.project import Project


T = TypeVar("T", bound="BigPlanFindResultEntry")


@_attrs_define
class BigPlanFindResultEntry:
    """A single big plan result.

    Attributes:
        big_plan (BigPlan): A big plan.
        note (Union['Note', None, Unset]):
        milestones (Union[None, Unset, list['BigPlanMilestone']]):
        stats (Union['BigPlanStats', None, Unset]):
        project (Union['Project', None, Unset]):
        inbox_tasks (Union[None, Unset, list['InboxTask']]):
    """

    big_plan: "BigPlan"
    note: Union["Note", None, Unset] = UNSET
    milestones: Union[None, Unset, list["BigPlanMilestone"]] = UNSET
    stats: Union["BigPlanStats", None, Unset] = UNSET
    project: Union["Project", None, Unset] = UNSET
    inbox_tasks: Union[None, Unset, list["InboxTask"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.big_plan_stats import BigPlanStats
        from ..models.note import Note
        from ..models.project import Project

        big_plan = self.big_plan.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        milestones: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.milestones, Unset):
            milestones = UNSET
        elif isinstance(self.milestones, list):
            milestones = []
            for milestones_type_0_item_data in self.milestones:
                milestones_type_0_item = milestones_type_0_item_data.to_dict()
                milestones.append(milestones_type_0_item)

        else:
            milestones = self.milestones

        stats: Union[None, Unset, dict[str, Any]]
        if isinstance(self.stats, Unset):
            stats = UNSET
        elif isinstance(self.stats, BigPlanStats):
            stats = self.stats.to_dict()
        else:
            stats = self.stats

        project: Union[None, Unset, dict[str, Any]]
        if isinstance(self.project, Unset):
            project = UNSET
        elif isinstance(self.project, Project):
            project = self.project.to_dict()
        else:
            project = self.project

        inbox_tasks: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.inbox_tasks, Unset):
            inbox_tasks = UNSET
        elif isinstance(self.inbox_tasks, list):
            inbox_tasks = []
            for inbox_tasks_type_0_item_data in self.inbox_tasks:
                inbox_tasks_type_0_item = inbox_tasks_type_0_item_data.to_dict()
                inbox_tasks.append(inbox_tasks_type_0_item)

        else:
            inbox_tasks = self.inbox_tasks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "big_plan": big_plan,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if milestones is not UNSET:
            field_dict["milestones"] = milestones
        if stats is not UNSET:
            field_dict["stats"] = stats
        if project is not UNSET:
            field_dict["project"] = project
        if inbox_tasks is not UNSET:
            field_dict["inbox_tasks"] = inbox_tasks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.big_plan_milestone import BigPlanMilestone
        from ..models.big_plan_stats import BigPlanStats
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.project import Project

        d = dict(src_dict)
        big_plan = BigPlan.from_dict(d.pop("big_plan"))

        def _parse_note(data: object) -> Union["Note", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Note", None, Unset], data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_milestones(data: object) -> Union[None, Unset, list["BigPlanMilestone"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                milestones_type_0 = []
                _milestones_type_0 = data
                for milestones_type_0_item_data in _milestones_type_0:
                    milestones_type_0_item = BigPlanMilestone.from_dict(milestones_type_0_item_data)

                    milestones_type_0.append(milestones_type_0_item)

                return milestones_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["BigPlanMilestone"]], data)

        milestones = _parse_milestones(d.pop("milestones", UNSET))

        def _parse_stats(data: object) -> Union["BigPlanStats", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                stats_type_0 = BigPlanStats.from_dict(data)

                return stats_type_0
            except:  # noqa: E722
                pass
            return cast(Union["BigPlanStats", None, Unset], data)

        stats = _parse_stats(d.pop("stats", UNSET))

        def _parse_project(data: object) -> Union["Project", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                project_type_0 = Project.from_dict(data)

                return project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Project", None, Unset], data)

        project = _parse_project(d.pop("project", UNSET))

        def _parse_inbox_tasks(data: object) -> Union[None, Unset, list["InboxTask"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                inbox_tasks_type_0 = []
                _inbox_tasks_type_0 = data
                for inbox_tasks_type_0_item_data in _inbox_tasks_type_0:
                    inbox_tasks_type_0_item = InboxTask.from_dict(inbox_tasks_type_0_item_data)

                    inbox_tasks_type_0.append(inbox_tasks_type_0_item)

                return inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["InboxTask"]], data)

        inbox_tasks = _parse_inbox_tasks(d.pop("inbox_tasks", UNSET))

        big_plan_find_result_entry = cls(
            big_plan=big_plan,
            note=note,
            milestones=milestones,
            stats=stats,
            project=project,
            inbox_tasks=inbox_tasks,
        )

        big_plan_find_result_entry.additional_properties = d
        return big_plan_find_result_entry

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
