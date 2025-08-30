from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan_summary import BigPlanSummary
    from ..models.chore_summary import ChoreSummary
    from ..models.habit_summary import HabitSummary
    from ..models.inbox_task_summary import InboxTaskSummary
    from ..models.journal_summary import JournalSummary
    from ..models.metric_summary import MetricSummary
    from ..models.person_summary import PersonSummary
    from ..models.project_summary import ProjectSummary
    from ..models.schedule_stream_summary import ScheduleStreamSummary
    from ..models.smart_list_summary import SmartListSummary
    from ..models.user import User
    from ..models.vacation_summary import VacationSummary
    from ..models.workspace import Workspace


T = TypeVar("T", bound="GetSummariesResult")


@_attrs_define
class GetSummariesResult:
    """Get summaries result.

    Attributes:
        user (Union['User', None, Unset]):
        workspace (Union['Workspace', None, Unset]):
        vacations (Union[None, Unset, list['VacationSummary']]):
        schedule_streams (Union[None, Unset, list['ScheduleStreamSummary']]):
        root_project (Union['ProjectSummary', None, Unset]):
        projects (Union[None, Unset, list['ProjectSummary']]):
        inbox_tasks (Union[None, Unset, list['InboxTaskSummary']]):
        journals_last_year (Union[None, Unset, list['JournalSummary']]):
        habits (Union[None, Unset, list['HabitSummary']]):
        chores (Union[None, Unset, list['ChoreSummary']]):
        big_plans (Union[None, Unset, list['BigPlanSummary']]):
        smart_lists (Union[None, Unset, list['SmartListSummary']]):
        metrics (Union[None, Unset, list['MetricSummary']]):
        persons (Union[None, Unset, list['PersonSummary']]):
    """

    user: Union["User", None, Unset] = UNSET
    workspace: Union["Workspace", None, Unset] = UNSET
    vacations: Union[None, Unset, list["VacationSummary"]] = UNSET
    schedule_streams: Union[None, Unset, list["ScheduleStreamSummary"]] = UNSET
    root_project: Union["ProjectSummary", None, Unset] = UNSET
    projects: Union[None, Unset, list["ProjectSummary"]] = UNSET
    inbox_tasks: Union[None, Unset, list["InboxTaskSummary"]] = UNSET
    journals_last_year: Union[None, Unset, list["JournalSummary"]] = UNSET
    habits: Union[None, Unset, list["HabitSummary"]] = UNSET
    chores: Union[None, Unset, list["ChoreSummary"]] = UNSET
    big_plans: Union[None, Unset, list["BigPlanSummary"]] = UNSET
    smart_lists: Union[None, Unset, list["SmartListSummary"]] = UNSET
    metrics: Union[None, Unset, list["MetricSummary"]] = UNSET
    persons: Union[None, Unset, list["PersonSummary"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.project_summary import ProjectSummary
        from ..models.user import User
        from ..models.workspace import Workspace

        user: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, User):
            user = self.user.to_dict()
        else:
            user = self.user

        workspace: Union[None, Unset, dict[str, Any]]
        if isinstance(self.workspace, Unset):
            workspace = UNSET
        elif isinstance(self.workspace, Workspace):
            workspace = self.workspace.to_dict()
        else:
            workspace = self.workspace

        vacations: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.vacations, Unset):
            vacations = UNSET
        elif isinstance(self.vacations, list):
            vacations = []
            for vacations_type_0_item_data in self.vacations:
                vacations_type_0_item = vacations_type_0_item_data.to_dict()
                vacations.append(vacations_type_0_item)

        else:
            vacations = self.vacations

        schedule_streams: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.schedule_streams, Unset):
            schedule_streams = UNSET
        elif isinstance(self.schedule_streams, list):
            schedule_streams = []
            for schedule_streams_type_0_item_data in self.schedule_streams:
                schedule_streams_type_0_item = schedule_streams_type_0_item_data.to_dict()
                schedule_streams.append(schedule_streams_type_0_item)

        else:
            schedule_streams = self.schedule_streams

        root_project: Union[None, Unset, dict[str, Any]]
        if isinstance(self.root_project, Unset):
            root_project = UNSET
        elif isinstance(self.root_project, ProjectSummary):
            root_project = self.root_project.to_dict()
        else:
            root_project = self.root_project

        projects: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.projects, Unset):
            projects = UNSET
        elif isinstance(self.projects, list):
            projects = []
            for projects_type_0_item_data in self.projects:
                projects_type_0_item = projects_type_0_item_data.to_dict()
                projects.append(projects_type_0_item)

        else:
            projects = self.projects

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

        journals_last_year: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.journals_last_year, Unset):
            journals_last_year = UNSET
        elif isinstance(self.journals_last_year, list):
            journals_last_year = []
            for journals_last_year_type_0_item_data in self.journals_last_year:
                journals_last_year_type_0_item = journals_last_year_type_0_item_data.to_dict()
                journals_last_year.append(journals_last_year_type_0_item)

        else:
            journals_last_year = self.journals_last_year

        habits: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.habits, Unset):
            habits = UNSET
        elif isinstance(self.habits, list):
            habits = []
            for habits_type_0_item_data in self.habits:
                habits_type_0_item = habits_type_0_item_data.to_dict()
                habits.append(habits_type_0_item)

        else:
            habits = self.habits

        chores: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.chores, Unset):
            chores = UNSET
        elif isinstance(self.chores, list):
            chores = []
            for chores_type_0_item_data in self.chores:
                chores_type_0_item = chores_type_0_item_data.to_dict()
                chores.append(chores_type_0_item)

        else:
            chores = self.chores

        big_plans: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.big_plans, Unset):
            big_plans = UNSET
        elif isinstance(self.big_plans, list):
            big_plans = []
            for big_plans_type_0_item_data in self.big_plans:
                big_plans_type_0_item = big_plans_type_0_item_data.to_dict()
                big_plans.append(big_plans_type_0_item)

        else:
            big_plans = self.big_plans

        smart_lists: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.smart_lists, Unset):
            smart_lists = UNSET
        elif isinstance(self.smart_lists, list):
            smart_lists = []
            for smart_lists_type_0_item_data in self.smart_lists:
                smart_lists_type_0_item = smart_lists_type_0_item_data.to_dict()
                smart_lists.append(smart_lists_type_0_item)

        else:
            smart_lists = self.smart_lists

        metrics: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.metrics, Unset):
            metrics = UNSET
        elif isinstance(self.metrics, list):
            metrics = []
            for metrics_type_0_item_data in self.metrics:
                metrics_type_0_item = metrics_type_0_item_data.to_dict()
                metrics.append(metrics_type_0_item)

        else:
            metrics = self.metrics

        persons: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.persons, Unset):
            persons = UNSET
        elif isinstance(self.persons, list):
            persons = []
            for persons_type_0_item_data in self.persons:
                persons_type_0_item = persons_type_0_item_data.to_dict()
                persons.append(persons_type_0_item)

        else:
            persons = self.persons

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user
        if workspace is not UNSET:
            field_dict["workspace"] = workspace
        if vacations is not UNSET:
            field_dict["vacations"] = vacations
        if schedule_streams is not UNSET:
            field_dict["schedule_streams"] = schedule_streams
        if root_project is not UNSET:
            field_dict["root_project"] = root_project
        if projects is not UNSET:
            field_dict["projects"] = projects
        if inbox_tasks is not UNSET:
            field_dict["inbox_tasks"] = inbox_tasks
        if journals_last_year is not UNSET:
            field_dict["journals_last_year"] = journals_last_year
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan_summary import BigPlanSummary
        from ..models.chore_summary import ChoreSummary
        from ..models.habit_summary import HabitSummary
        from ..models.inbox_task_summary import InboxTaskSummary
        from ..models.journal_summary import JournalSummary
        from ..models.metric_summary import MetricSummary
        from ..models.person_summary import PersonSummary
        from ..models.project_summary import ProjectSummary
        from ..models.schedule_stream_summary import ScheduleStreamSummary
        from ..models.smart_list_summary import SmartListSummary
        from ..models.user import User
        from ..models.vacation_summary import VacationSummary
        from ..models.workspace import Workspace

        d = dict(src_dict)

        def _parse_user(data: object) -> Union["User", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_type_0 = User.from_dict(data)

                return user_type_0
            except:  # noqa: E722
                pass
            return cast(Union["User", None, Unset], data)

        user = _parse_user(d.pop("user", UNSET))

        def _parse_workspace(data: object) -> Union["Workspace", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                workspace_type_0 = Workspace.from_dict(data)

                return workspace_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Workspace", None, Unset], data)

        workspace = _parse_workspace(d.pop("workspace", UNSET))

        def _parse_vacations(data: object) -> Union[None, Unset, list["VacationSummary"]]:
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
            return cast(Union[None, Unset, list["VacationSummary"]], data)

        vacations = _parse_vacations(d.pop("vacations", UNSET))

        def _parse_schedule_streams(data: object) -> Union[None, Unset, list["ScheduleStreamSummary"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                schedule_streams_type_0 = []
                _schedule_streams_type_0 = data
                for schedule_streams_type_0_item_data in _schedule_streams_type_0:
                    schedule_streams_type_0_item = ScheduleStreamSummary.from_dict(schedule_streams_type_0_item_data)

                    schedule_streams_type_0.append(schedule_streams_type_0_item)

                return schedule_streams_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ScheduleStreamSummary"]], data)

        schedule_streams = _parse_schedule_streams(d.pop("schedule_streams", UNSET))

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

        def _parse_projects(data: object) -> Union[None, Unset, list["ProjectSummary"]]:
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
            return cast(Union[None, Unset, list["ProjectSummary"]], data)

        projects = _parse_projects(d.pop("projects", UNSET))

        def _parse_inbox_tasks(data: object) -> Union[None, Unset, list["InboxTaskSummary"]]:
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
            return cast(Union[None, Unset, list["InboxTaskSummary"]], data)

        inbox_tasks = _parse_inbox_tasks(d.pop("inbox_tasks", UNSET))

        def _parse_journals_last_year(data: object) -> Union[None, Unset, list["JournalSummary"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                journals_last_year_type_0 = []
                _journals_last_year_type_0 = data
                for journals_last_year_type_0_item_data in _journals_last_year_type_0:
                    journals_last_year_type_0_item = JournalSummary.from_dict(journals_last_year_type_0_item_data)

                    journals_last_year_type_0.append(journals_last_year_type_0_item)

                return journals_last_year_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["JournalSummary"]], data)

        journals_last_year = _parse_journals_last_year(d.pop("journals_last_year", UNSET))

        def _parse_habits(data: object) -> Union[None, Unset, list["HabitSummary"]]:
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
            return cast(Union[None, Unset, list["HabitSummary"]], data)

        habits = _parse_habits(d.pop("habits", UNSET))

        def _parse_chores(data: object) -> Union[None, Unset, list["ChoreSummary"]]:
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
            return cast(Union[None, Unset, list["ChoreSummary"]], data)

        chores = _parse_chores(d.pop("chores", UNSET))

        def _parse_big_plans(data: object) -> Union[None, Unset, list["BigPlanSummary"]]:
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
            return cast(Union[None, Unset, list["BigPlanSummary"]], data)

        big_plans = _parse_big_plans(d.pop("big_plans", UNSET))

        def _parse_smart_lists(data: object) -> Union[None, Unset, list["SmartListSummary"]]:
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
            return cast(Union[None, Unset, list["SmartListSummary"]], data)

        smart_lists = _parse_smart_lists(d.pop("smart_lists", UNSET))

        def _parse_metrics(data: object) -> Union[None, Unset, list["MetricSummary"]]:
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
            return cast(Union[None, Unset, list["MetricSummary"]], data)

        metrics = _parse_metrics(d.pop("metrics", UNSET))

        def _parse_persons(data: object) -> Union[None, Unset, list["PersonSummary"]]:
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
            return cast(Union[None, Unset, list["PersonSummary"]], data)

        persons = _parse_persons(d.pop("persons", UNSET))

        get_summaries_result = cls(
            user=user,
            workspace=workspace,
            vacations=vacations,
            schedule_streams=schedule_streams,
            root_project=root_project,
            projects=projects,
            inbox_tasks=inbox_tasks,
            journals_last_year=journals_last_year,
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
