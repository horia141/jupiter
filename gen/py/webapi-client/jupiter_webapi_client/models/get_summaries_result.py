from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan_summary import BigPlanSummary
    from ..models.chore_summary import ChoreSummary
    from ..models.habit_summary import HabitSummary
    from ..models.inbox_task_summary import InboxTaskSummary
    from ..models.metric_summary import MetricSummary
    from ..models.person_summary import PersonSummary
    from ..models.project_summary import ProjectSummary
    from ..models.smart_list_summary import SmartListSummary
    from ..models.vacation_summary import VacationSummary


T = TypeVar("T", bound="GetSummariesResult")


@_attrs_define
class GetSummariesResult:
    """Get summaries result.

    Attributes:
        vacations (Union[Unset, List['VacationSummary']]):
        root_project (Union[Unset, ProjectSummary]): Summary information about a project.
        projects (Union[Unset, List['ProjectSummary']]):
        inbox_tasks (Union[Unset, List['InboxTaskSummary']]):
        habits (Union[Unset, List['HabitSummary']]):
        chores (Union[Unset, List['ChoreSummary']]):
        big_plans (Union[Unset, List['BigPlanSummary']]):
        smart_lists (Union[Unset, List['SmartListSummary']]):
        metrics (Union[Unset, List['MetricSummary']]):
        persons (Union[Unset, List['PersonSummary']]):
    """

    vacations: Union[Unset, List["VacationSummary"]] = UNSET
    root_project: Union[Unset, "ProjectSummary"] = UNSET
    projects: Union[Unset, List["ProjectSummary"]] = UNSET
    inbox_tasks: Union[Unset, List["InboxTaskSummary"]] = UNSET
    habits: Union[Unset, List["HabitSummary"]] = UNSET
    chores: Union[Unset, List["ChoreSummary"]] = UNSET
    big_plans: Union[Unset, List["BigPlanSummary"]] = UNSET
    smart_lists: Union[Unset, List["SmartListSummary"]] = UNSET
    metrics: Union[Unset, List["MetricSummary"]] = UNSET
    persons: Union[Unset, List["PersonSummary"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        vacations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.vacations, Unset):
            vacations = []
            for vacations_item_data in self.vacations:
                vacations_item = vacations_item_data.to_dict()
                vacations.append(vacations_item)

        root_project: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.root_project, Unset):
            root_project = self.root_project.to_dict()

        projects: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.projects, Unset):
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()
                projects.append(projects_item)

        inbox_tasks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.inbox_tasks, Unset):
            inbox_tasks = []
            for inbox_tasks_item_data in self.inbox_tasks:
                inbox_tasks_item = inbox_tasks_item_data.to_dict()
                inbox_tasks.append(inbox_tasks_item)

        habits: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.habits, Unset):
            habits = []
            for habits_item_data in self.habits:
                habits_item = habits_item_data.to_dict()
                habits.append(habits_item)

        chores: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.chores, Unset):
            chores = []
            for chores_item_data in self.chores:
                chores_item = chores_item_data.to_dict()
                chores.append(chores_item)

        big_plans: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.big_plans, Unset):
            big_plans = []
            for big_plans_item_data in self.big_plans:
                big_plans_item = big_plans_item_data.to_dict()
                big_plans.append(big_plans_item)

        smart_lists: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.smart_lists, Unset):
            smart_lists = []
            for smart_lists_item_data in self.smart_lists:
                smart_lists_item = smart_lists_item_data.to_dict()
                smart_lists.append(smart_lists_item)

        metrics: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = []
            for metrics_item_data in self.metrics:
                metrics_item = metrics_item_data.to_dict()
                metrics.append(metrics_item)

        persons: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.persons, Unset):
            persons = []
            for persons_item_data in self.persons:
                persons_item = persons_item_data.to_dict()
                persons.append(persons_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vacations is not UNSET:
            field_dict["vacations"] = vacations
        if root_project is not UNSET:
            field_dict["root_project"] = root_project
        if projects is not UNSET:
            field_dict["projects"] = projects
        if inbox_tasks is not UNSET:
            field_dict["inbox_tasks"] = inbox_tasks
        if habits is not UNSET:
            field_dict["habits"] = habits
        if chores is not UNSET:
            field_dict["chores"] = chores
        if big_plans is not UNSET:
            field_dict["big_plans"] = big_plans
        if smart_lists is not UNSET:
            field_dict["smart_lists"] = smart_lists
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if persons is not UNSET:
            field_dict["persons"] = persons

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.big_plan_summary import BigPlanSummary
        from ..models.chore_summary import ChoreSummary
        from ..models.habit_summary import HabitSummary
        from ..models.inbox_task_summary import InboxTaskSummary
        from ..models.metric_summary import MetricSummary
        from ..models.person_summary import PersonSummary
        from ..models.project_summary import ProjectSummary
        from ..models.smart_list_summary import SmartListSummary
        from ..models.vacation_summary import VacationSummary

        d = src_dict.copy()
        vacations = []
        _vacations = d.pop("vacations", UNSET)
        for vacations_item_data in _vacations or []:
            vacations_item = VacationSummary.from_dict(vacations_item_data)

            vacations.append(vacations_item)

        _root_project = d.pop("root_project", UNSET)
        root_project: Union[Unset, ProjectSummary]
        if isinstance(_root_project, Unset):
            root_project = UNSET
        else:
            root_project = ProjectSummary.from_dict(_root_project)

        projects = []
        _projects = d.pop("projects", UNSET)
        for projects_item_data in _projects or []:
            projects_item = ProjectSummary.from_dict(projects_item_data)

            projects.append(projects_item)

        inbox_tasks = []
        _inbox_tasks = d.pop("inbox_tasks", UNSET)
        for inbox_tasks_item_data in _inbox_tasks or []:
            inbox_tasks_item = InboxTaskSummary.from_dict(inbox_tasks_item_data)

            inbox_tasks.append(inbox_tasks_item)

        habits = []
        _habits = d.pop("habits", UNSET)
        for habits_item_data in _habits or []:
            habits_item = HabitSummary.from_dict(habits_item_data)

            habits.append(habits_item)

        chores = []
        _chores = d.pop("chores", UNSET)
        for chores_item_data in _chores or []:
            chores_item = ChoreSummary.from_dict(chores_item_data)

            chores.append(chores_item)

        big_plans = []
        _big_plans = d.pop("big_plans", UNSET)
        for big_plans_item_data in _big_plans or []:
            big_plans_item = BigPlanSummary.from_dict(big_plans_item_data)

            big_plans.append(big_plans_item)

        smart_lists = []
        _smart_lists = d.pop("smart_lists", UNSET)
        for smart_lists_item_data in _smart_lists or []:
            smart_lists_item = SmartListSummary.from_dict(smart_lists_item_data)

            smart_lists.append(smart_lists_item)

        metrics = []
        _metrics = d.pop("metrics", UNSET)
        for metrics_item_data in _metrics or []:
            metrics_item = MetricSummary.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        persons = []
        _persons = d.pop("persons", UNSET)
        for persons_item_data in _persons or []:
            persons_item = PersonSummary.from_dict(persons_item_data)

            persons.append(persons_item)

        get_summaries_result = cls(
            vacations=vacations,
            root_project=root_project,
            projects=projects,
            inbox_tasks=inbox_tasks,
            habits=habits,
            chores=chores,
            big_plans=big_plans,
            smart_lists=smart_lists,
            metrics=metrics,
            persons=persons,
        )

        get_summaries_result.additional_properties = d
        return get_summaries_result

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
