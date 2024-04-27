from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

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
        vacations (Union[List['VacationSummary'], None, Unset]):
        root_project (Union['ProjectSummary', None, Unset]):
        projects (Union[List['ProjectSummary'], None, Unset]):
        inbox_tasks (Union[List['InboxTaskSummary'], None, Unset]):
        habits (Union[List['HabitSummary'], None, Unset]):
        chores (Union[List['ChoreSummary'], None, Unset]):
        big_plans (Union[List['BigPlanSummary'], None, Unset]):
        smart_lists (Union[List['SmartListSummary'], None, Unset]):
        metrics (Union[List['MetricSummary'], None, Unset]):
        persons (Union[List['PersonSummary'], None, Unset]):
    """

    vacations: Union[List["VacationSummary"], None, Unset] = UNSET
    root_project: Union["ProjectSummary", None, Unset] = UNSET
    projects: Union[List["ProjectSummary"], None, Unset] = UNSET
    inbox_tasks: Union[List["InboxTaskSummary"], None, Unset] = UNSET
    habits: Union[List["HabitSummary"], None, Unset] = UNSET
    chores: Union[List["ChoreSummary"], None, Unset] = UNSET
    big_plans: Union[List["BigPlanSummary"], None, Unset] = UNSET
    smart_lists: Union[List["SmartListSummary"], None, Unset] = UNSET
    metrics: Union[List["MetricSummary"], None, Unset] = UNSET
    persons: Union[List["PersonSummary"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.project_summary import ProjectSummary

        vacations: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.vacations, Unset):
            vacations = UNSET
        elif isinstance(self.vacations, list):
            vacations = []
            for vacations_type_0_item_data in self.vacations:
                vacations_type_0_item = vacations_type_0_item_data.to_dict()
                vacations.append(vacations_type_0_item)

        else:
            vacations = self.vacations

        root_project: Union[Dict[str, Any], None, Unset]
        if isinstance(self.root_project, Unset):
            root_project = UNSET
        elif isinstance(self.root_project, ProjectSummary):
            root_project = self.root_project.to_dict()
        else:
            root_project = self.root_project

        projects: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.projects, Unset):
            projects = UNSET
        elif isinstance(self.projects, list):
            projects = []
            for projects_type_0_item_data in self.projects:
                projects_type_0_item = projects_type_0_item_data.to_dict()
                projects.append(projects_type_0_item)

        else:
            projects = self.projects

        inbox_tasks: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.inbox_tasks, Unset):
            inbox_tasks = UNSET
        elif isinstance(self.inbox_tasks, list):
            inbox_tasks = []
            for inbox_tasks_type_0_item_data in self.inbox_tasks:
                inbox_tasks_type_0_item = inbox_tasks_type_0_item_data.to_dict()
                inbox_tasks.append(inbox_tasks_type_0_item)

        else:
            inbox_tasks = self.inbox_tasks

        habits: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.habits, Unset):
            habits = UNSET
        elif isinstance(self.habits, list):
            habits = []
            for habits_type_0_item_data in self.habits:
                habits_type_0_item = habits_type_0_item_data.to_dict()
                habits.append(habits_type_0_item)

        else:
            habits = self.habits

        chores: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.chores, Unset):
            chores = UNSET
        elif isinstance(self.chores, list):
            chores = []
            for chores_type_0_item_data in self.chores:
                chores_type_0_item = chores_type_0_item_data.to_dict()
                chores.append(chores_type_0_item)

        else:
            chores = self.chores

        big_plans: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.big_plans, Unset):
            big_plans = UNSET
        elif isinstance(self.big_plans, list):
            big_plans = []
            for big_plans_type_0_item_data in self.big_plans:
                big_plans_type_0_item = big_plans_type_0_item_data.to_dict()
                big_plans.append(big_plans_type_0_item)

        else:
            big_plans = self.big_plans

        smart_lists: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.smart_lists, Unset):
            smart_lists = UNSET
        elif isinstance(self.smart_lists, list):
            smart_lists = []
            for smart_lists_type_0_item_data in self.smart_lists:
                smart_lists_type_0_item = smart_lists_type_0_item_data.to_dict()
                smart_lists.append(smart_lists_type_0_item)

        else:
            smart_lists = self.smart_lists

        metrics: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.metrics, Unset):
            metrics = UNSET
        elif isinstance(self.metrics, list):
            metrics = []
            for metrics_type_0_item_data in self.metrics:
                metrics_type_0_item = metrics_type_0_item_data.to_dict()
                metrics.append(metrics_type_0_item)

        else:
            metrics = self.metrics

        persons: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.persons, Unset):
            persons = UNSET
        elif isinstance(self.persons, list):
            persons = []
            for persons_type_0_item_data in self.persons:
                persons_type_0_item = persons_type_0_item_data.to_dict()
                persons.append(persons_type_0_item)

        else:
            persons = self.persons

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

        def _parse_vacations(data: object) -> Union[List["VacationSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                vacations_type_0 = []
                _vacations_type_0 = data
                for vacations_type_0_item_data in _vacations_type_0:
                    vacations_type_0_item = VacationSummary.from_dict(vacations_type_0_item_data)

                    vacations_type_0.append(vacations_type_0_item)

                return vacations_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["VacationSummary"], None, Unset], data)

        vacations = _parse_vacations(d.pop("vacations", UNSET))

        def _parse_root_project(data: object) -> Union["ProjectSummary", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                root_project_type_0 = ProjectSummary.from_dict(data)

                return root_project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ProjectSummary", None, Unset], data)

        root_project = _parse_root_project(d.pop("root_project", UNSET))

        def _parse_projects(data: object) -> Union[List["ProjectSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                projects_type_0 = []
                _projects_type_0 = data
                for projects_type_0_item_data in _projects_type_0:
                    projects_type_0_item = ProjectSummary.from_dict(projects_type_0_item_data)

                    projects_type_0.append(projects_type_0_item)

                return projects_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["ProjectSummary"], None, Unset], data)

        projects = _parse_projects(d.pop("projects", UNSET))

        def _parse_inbox_tasks(data: object) -> Union[List["InboxTaskSummary"], None, Unset]:
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
                    inbox_tasks_type_0_item = InboxTaskSummary.from_dict(inbox_tasks_type_0_item_data)

                    inbox_tasks_type_0.append(inbox_tasks_type_0_item)

                return inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["InboxTaskSummary"], None, Unset], data)

        inbox_tasks = _parse_inbox_tasks(d.pop("inbox_tasks", UNSET))

        def _parse_habits(data: object) -> Union[List["HabitSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                habits_type_0 = []
                _habits_type_0 = data
                for habits_type_0_item_data in _habits_type_0:
                    habits_type_0_item = HabitSummary.from_dict(habits_type_0_item_data)

                    habits_type_0.append(habits_type_0_item)

                return habits_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["HabitSummary"], None, Unset], data)

        habits = _parse_habits(d.pop("habits", UNSET))

        def _parse_chores(data: object) -> Union[List["ChoreSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                chores_type_0 = []
                _chores_type_0 = data
                for chores_type_0_item_data in _chores_type_0:
                    chores_type_0_item = ChoreSummary.from_dict(chores_type_0_item_data)

                    chores_type_0.append(chores_type_0_item)

                return chores_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["ChoreSummary"], None, Unset], data)

        chores = _parse_chores(d.pop("chores", UNSET))

        def _parse_big_plans(data: object) -> Union[List["BigPlanSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                big_plans_type_0 = []
                _big_plans_type_0 = data
                for big_plans_type_0_item_data in _big_plans_type_0:
                    big_plans_type_0_item = BigPlanSummary.from_dict(big_plans_type_0_item_data)

                    big_plans_type_0.append(big_plans_type_0_item)

                return big_plans_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["BigPlanSummary"], None, Unset], data)

        big_plans = _parse_big_plans(d.pop("big_plans", UNSET))

        def _parse_smart_lists(data: object) -> Union[List["SmartListSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                smart_lists_type_0 = []
                _smart_lists_type_0 = data
                for smart_lists_type_0_item_data in _smart_lists_type_0:
                    smart_lists_type_0_item = SmartListSummary.from_dict(smart_lists_type_0_item_data)

                    smart_lists_type_0.append(smart_lists_type_0_item)

                return smart_lists_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["SmartListSummary"], None, Unset], data)

        smart_lists = _parse_smart_lists(d.pop("smart_lists", UNSET))

        def _parse_metrics(data: object) -> Union[List["MetricSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                metrics_type_0 = []
                _metrics_type_0 = data
                for metrics_type_0_item_data in _metrics_type_0:
                    metrics_type_0_item = MetricSummary.from_dict(metrics_type_0_item_data)

                    metrics_type_0.append(metrics_type_0_item)

                return metrics_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["MetricSummary"], None, Unset], data)

        metrics = _parse_metrics(d.pop("metrics", UNSET))

        def _parse_persons(data: object) -> Union[List["PersonSummary"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                persons_type_0 = []
                _persons_type_0 = data
                for persons_type_0_item_data in _persons_type_0:
                    persons_type_0_item = PersonSummary.from_dict(persons_type_0_item_data)

                    persons_type_0.append(persons_type_0_item)

                return persons_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["PersonSummary"], None, Unset], data)

        persons = _parse_persons(d.pop("persons", UNSET))

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
