from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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
    from ..models.time_event_in_day_block import TimeEventInDayBlock
    from ..models.working_mem import WorkingMem


T = TypeVar("T", bound="InboxTaskLoadResult")


@_attrs_define
class InboxTaskLoadResult:
    """InboxTaskLoadResult.

    Attributes:
        inbox_task (InboxTask): An inbox task.
        project (Project): The project.
        time_event_blocks (list['TimeEventInDayBlock']):
        working_mem (Union['WorkingMem', None, Unset]):
        habit (Union['Habit', None, Unset]):
        chore (Union['Chore', None, Unset]):
        big_plan (Union['BigPlan', None, Unset]):
        metric (Union['Metric', None, Unset]):
        person (Union['Person', None, Unset]):
        slack_task (Union['SlackTask', None, Unset]):
        email_task (Union['EmailTask', None, Unset]):
        note (Union['Note', None, Unset]):
    """

    inbox_task: "InboxTask"
    project: "Project"
    time_event_blocks: list["TimeEventInDayBlock"]
    working_mem: Union["WorkingMem", None, Unset] = UNSET
    habit: Union["Habit", None, Unset] = UNSET
    chore: Union["Chore", None, Unset] = UNSET
    big_plan: Union["BigPlan", None, Unset] = UNSET
    metric: Union["Metric", None, Unset] = UNSET
    person: Union["Person", None, Unset] = UNSET
    slack_task: Union["SlackTask", None, Unset] = UNSET
    email_task: Union["EmailTask", None, Unset] = UNSET
    note: Union["Note", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.big_plan import BigPlan
        from ..models.chore import Chore
        from ..models.email_task import EmailTask
        from ..models.habit import Habit
        from ..models.metric import Metric
        from ..models.note import Note
        from ..models.person import Person
        from ..models.slack_task import SlackTask
        from ..models.working_mem import WorkingMem

        inbox_task = self.inbox_task.to_dict()

        project = self.project.to_dict()

        time_event_blocks = []
        for time_event_blocks_item_data in self.time_event_blocks:
            time_event_blocks_item = time_event_blocks_item_data.to_dict()
            time_event_blocks.append(time_event_blocks_item)

        working_mem: Union[None, Unset, dict[str, Any]]
        if isinstance(self.working_mem, Unset):
            working_mem = UNSET
        elif isinstance(self.working_mem, WorkingMem):
            working_mem = self.working_mem.to_dict()
        else:
            working_mem = self.working_mem

        habit: Union[None, Unset, dict[str, Any]]
        if isinstance(self.habit, Unset):
            habit = UNSET
        elif isinstance(self.habit, Habit):
            habit = self.habit.to_dict()
        else:
            habit = self.habit

        chore: Union[None, Unset, dict[str, Any]]
        if isinstance(self.chore, Unset):
            chore = UNSET
        elif isinstance(self.chore, Chore):
            chore = self.chore.to_dict()
        else:
            chore = self.chore

        big_plan: Union[None, Unset, dict[str, Any]]
        if isinstance(self.big_plan, Unset):
            big_plan = UNSET
        elif isinstance(self.big_plan, BigPlan):
            big_plan = self.big_plan.to_dict()
        else:
            big_plan = self.big_plan

        metric: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metric, Unset):
            metric = UNSET
        elif isinstance(self.metric, Metric):
            metric = self.metric.to_dict()
        else:
            metric = self.metric

        person: Union[None, Unset, dict[str, Any]]
        if isinstance(self.person, Unset):
            person = UNSET
        elif isinstance(self.person, Person):
            person = self.person.to_dict()
        else:
            person = self.person

        slack_task: Union[None, Unset, dict[str, Any]]
        if isinstance(self.slack_task, Unset):
            slack_task = UNSET
        elif isinstance(self.slack_task, SlackTask):
            slack_task = self.slack_task.to_dict()
        else:
            slack_task = self.slack_task

        email_task: Union[None, Unset, dict[str, Any]]
        if isinstance(self.email_task, Unset):
            email_task = UNSET
        elif isinstance(self.email_task, EmailTask):
            email_task = self.email_task.to_dict()
        else:
            email_task = self.email_task

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbox_task": inbox_task,
                "project": project,
                "time_event_blocks": time_event_blocks,
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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
        from ..models.time_event_in_day_block import TimeEventInDayBlock
        from ..models.working_mem import WorkingMem

        d = dict(src_dict)
        inbox_task = InboxTask.from_dict(d.pop("inbox_task"))

        project = Project.from_dict(d.pop("project"))

        time_event_blocks = []
        _time_event_blocks = d.pop("time_event_blocks")
        for time_event_blocks_item_data in _time_event_blocks:
            time_event_blocks_item = TimeEventInDayBlock.from_dict(time_event_blocks_item_data)

            time_event_blocks.append(time_event_blocks_item)

        def _parse_working_mem(data: object) -> Union["WorkingMem", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                working_mem_type_0 = WorkingMem.from_dict(data)

                return working_mem_type_0
            except:  # noqa: E722
                pass
            return cast(Union["WorkingMem", None, Unset], data)

        working_mem = _parse_working_mem(d.pop("working_mem", UNSET))

        def _parse_habit(data: object) -> Union["Habit", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                habit_type_0 = Habit.from_dict(data)

                return habit_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Habit", None, Unset], data)

        habit = _parse_habit(d.pop("habit", UNSET))

        def _parse_chore(data: object) -> Union["Chore", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                chore_type_0 = Chore.from_dict(data)

                return chore_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Chore", None, Unset], data)

        chore = _parse_chore(d.pop("chore", UNSET))

        def _parse_big_plan(data: object) -> Union["BigPlan", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                big_plan_type_0 = BigPlan.from_dict(data)

                return big_plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union["BigPlan", None, Unset], data)

        big_plan = _parse_big_plan(d.pop("big_plan", UNSET))

        def _parse_metric(data: object) -> Union["Metric", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metric_type_0 = Metric.from_dict(data)

                return metric_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Metric", None, Unset], data)

        metric = _parse_metric(d.pop("metric", UNSET))

        def _parse_person(data: object) -> Union["Person", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                person_type_0 = Person.from_dict(data)

                return person_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Person", None, Unset], data)

        person = _parse_person(d.pop("person", UNSET))

        def _parse_slack_task(data: object) -> Union["SlackTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                slack_task_type_0 = SlackTask.from_dict(data)

                return slack_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SlackTask", None, Unset], data)

        slack_task = _parse_slack_task(d.pop("slack_task", UNSET))

        def _parse_email_task(data: object) -> Union["EmailTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                email_task_type_0 = EmailTask.from_dict(data)

                return email_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EmailTask", None, Unset], data)

        email_task = _parse_email_task(d.pop("email_task", UNSET))

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

        inbox_task_load_result = cls(
            inbox_task=inbox_task,
            project=project,
            time_event_blocks=time_event_blocks,
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
