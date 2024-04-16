from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.chore import Chore
    from ..models.email_task import EmailTask
    from ..models.habit import Habit
    from ..models.inbox_task import InboxTask
    from ..models.metric import Metric
    from ..models.note import Note
    from ..models.person import Person
    from ..models.project import Project
    from ..models.slack_task import SlackTask
    from ..models.working_mem import WorkingMem


T = TypeVar("T", bound="InboxTaskLoadResult")


@_attrs_define
class InboxTaskLoadResult:
    """InboxTaskLoadResult.

    Attributes:
        inbox_task (InboxTask): An inbox task.
        project (Project): The project.
        working_mem (Union[Unset, WorkingMem]): An entry in the working_mem.txt system.
        habit (Union[Unset, Habit]): A habit.
        chore (Union[Unset, Chore]): A chore.
        big_plan (Union[Unset, BigPlan]): A big plan.
        metric (Union[Unset, Metric]): A metric.
        person (Union[Unset, Person]): A person.
        slack_task (Union[Unset, SlackTask]): A Slack task which needs to be converted into an inbox task.
        email_task (Union[Unset, EmailTask]): An email task which needs to be converted into an inbox task.
        note (Union[Unset, Note]): A note in the notebook.
    """

    inbox_task: "InboxTask"
    project: "Project"
    working_mem: Union[Unset, "WorkingMem"] = UNSET
    habit: Union[Unset, "Habit"] = UNSET
    chore: Union[Unset, "Chore"] = UNSET
    big_plan: Union[Unset, "BigPlan"] = UNSET
    metric: Union[Unset, "Metric"] = UNSET
    person: Union[Unset, "Person"] = UNSET
    slack_task: Union[Unset, "SlackTask"] = UNSET
    email_task: Union[Unset, "EmailTask"] = UNSET
    note: Union[Unset, "Note"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inbox_task = self.inbox_task.to_dict()

        project = self.project.to_dict()

        working_mem: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.working_mem, Unset):
            working_mem = self.working_mem.to_dict()

        habit: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.habit, Unset):
            habit = self.habit.to_dict()

        chore: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.chore, Unset):
            chore = self.chore.to_dict()

        big_plan: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.big_plan, Unset):
            big_plan = self.big_plan.to_dict()

        metric: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metric, Unset):
            metric = self.metric.to_dict()

        person: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.person, Unset):
            person = self.person.to_dict()

        slack_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.slack_task, Unset):
            slack_task = self.slack_task.to_dict()

        email_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.email_task, Unset):
            email_task = self.email_task.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbox_task": inbox_task,
                "project": project,
            }
        )
        if working_mem is not UNSET:
            field_dict["working_mem"] = working_mem
        if habit is not UNSET:
            field_dict["habit"] = habit
        if chore is not UNSET:
            field_dict["chore"] = chore
        if big_plan is not UNSET:
            field_dict["big_plan"] = big_plan
        if metric is not UNSET:
            field_dict["metric"] = metric
        if person is not UNSET:
            field_dict["person"] = person
        if slack_task is not UNSET:
            field_dict["slack_task"] = slack_task
        if email_task is not UNSET:
            field_dict["email_task"] = email_task
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.chore import Chore
        from ..models.email_task import EmailTask
        from ..models.habit import Habit
        from ..models.inbox_task import InboxTask
        from ..models.metric import Metric
        from ..models.note import Note
        from ..models.person import Person
        from ..models.project import Project
        from ..models.slack_task import SlackTask
        from ..models.working_mem import WorkingMem

        d = src_dict.copy()
        inbox_task = InboxTask.from_dict(d.pop("inbox_task"))

        project = Project.from_dict(d.pop("project"))

        _working_mem = d.pop("working_mem", UNSET)
        working_mem: Union[Unset, WorkingMem]
        if isinstance(_working_mem, Unset):
            working_mem = UNSET
        else:
            working_mem = WorkingMem.from_dict(_working_mem)

        _habit = d.pop("habit", UNSET)
        habit: Union[Unset, Habit]
        if isinstance(_habit, Unset):
            habit = UNSET
        else:
            habit = Habit.from_dict(_habit)

        _chore = d.pop("chore", UNSET)
        chore: Union[Unset, Chore]
        if isinstance(_chore, Unset):
            chore = UNSET
        else:
            chore = Chore.from_dict(_chore)

        _big_plan = d.pop("big_plan", UNSET)
        big_plan: Union[Unset, BigPlan]
        if isinstance(_big_plan, Unset):
            big_plan = UNSET
        else:
            big_plan = BigPlan.from_dict(_big_plan)

        _metric = d.pop("metric", UNSET)
        metric: Union[Unset, Metric]
        if isinstance(_metric, Unset):
            metric = UNSET
        else:
            metric = Metric.from_dict(_metric)

        _person = d.pop("person", UNSET)
        person: Union[Unset, Person]
        if isinstance(_person, Unset):
            person = UNSET
        else:
            person = Person.from_dict(_person)

        _slack_task = d.pop("slack_task", UNSET)
        slack_task: Union[Unset, SlackTask]
        if isinstance(_slack_task, Unset):
            slack_task = UNSET
        else:
            slack_task = SlackTask.from_dict(_slack_task)

        _email_task = d.pop("email_task", UNSET)
        email_task: Union[Unset, EmailTask]
        if isinstance(_email_task, Unset):
            email_task = UNSET
        else:
            email_task = EmailTask.from_dict(_email_task)

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        inbox_task_load_result = cls(
            inbox_task=inbox_task,
            project=project,
            working_mem=working_mem,
            habit=habit,
            chore=chore,
            big_plan=big_plan,
            metric=metric,
            person=person,
            slack_task=slack_task,
            email_task=email_task,
            note=note,
        )

        inbox_task_load_result.additional_properties = d
        return inbox_task_load_result

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
