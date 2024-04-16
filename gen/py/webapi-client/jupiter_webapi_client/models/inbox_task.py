from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.inbox_task_source import InboxTaskSource
from ..models.inbox_task_status import InboxTaskStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="InboxTask")


@_attrs_define
class InboxTask:
    """An inbox task.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name of an inbox task.
        inbox_task_collection (str):
        source (InboxTaskSource): The origin of an inbox task.
        project_ref_id (str): A generic entity id.
        status (InboxTaskStatus): The status of an inbox task.
        eisen (Eisen): The Eisenhower status of a particular task.
        archived_time (Union[Unset, str]): A timestamp in the application.
        difficulty (Union[Unset, Difficulty]): The difficulty of a particular task.
        actionable_date (Union[Unset, str]): A date or possibly a datetime for the application.
        due_date (Union[Unset, str]): A date or possibly a datetime for the application.
        notes (Union[Unset, str]):
        working_mem_ref_id (Union[Unset, str]): A generic entity id.
        habit_ref_id (Union[Unset, str]): A generic entity id.
        chore_ref_id (Union[Unset, str]): A generic entity id.
        big_plan_ref_id (Union[Unset, str]): A generic entity id.
        journal_ref_id (Union[Unset, str]): A generic entity id.
        metric_ref_id (Union[Unset, str]): A generic entity id.
        person_ref_id (Union[Unset, str]): A generic entity id.
        slack_task_ref_id (Union[Unset, str]): A generic entity id.
        email_task_ref_id (Union[Unset, str]): A generic entity id.
        recurring_timeline (Union[Unset, str]):
        recurring_repeat_index (Union[Unset, int]):
        recurring_gen_right_now (Union[Unset, str]): A timestamp in the application.
        accepted_time (Union[Unset, str]): A timestamp in the application.
        working_time (Union[Unset, str]): A timestamp in the application.
        completed_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    inbox_task_collection: str
    source: InboxTaskSource
    project_ref_id: str
    status: InboxTaskStatus
    eisen: Eisen
    archived_time: Union[Unset, str] = UNSET
    difficulty: Union[Unset, Difficulty] = UNSET
    actionable_date: Union[Unset, str] = UNSET
    due_date: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    working_mem_ref_id: Union[Unset, str] = UNSET
    habit_ref_id: Union[Unset, str] = UNSET
    chore_ref_id: Union[Unset, str] = UNSET
    big_plan_ref_id: Union[Unset, str] = UNSET
    journal_ref_id: Union[Unset, str] = UNSET
    metric_ref_id: Union[Unset, str] = UNSET
    person_ref_id: Union[Unset, str] = UNSET
    slack_task_ref_id: Union[Unset, str] = UNSET
    email_task_ref_id: Union[Unset, str] = UNSET
    recurring_timeline: Union[Unset, str] = UNSET
    recurring_repeat_index: Union[Unset, int] = UNSET
    recurring_gen_right_now: Union[Unset, str] = UNSET
    accepted_time: Union[Unset, str] = UNSET
    working_time: Union[Unset, str] = UNSET
    completed_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        inbox_task_collection = self.inbox_task_collection

        source = self.source.value

        project_ref_id = self.project_ref_id

        status = self.status.value

        eisen = self.eisen.value

        archived_time = self.archived_time

        difficulty: Union[Unset, str] = UNSET
        if not isinstance(self.difficulty, Unset):
            difficulty = self.difficulty.value

        actionable_date = self.actionable_date

        due_date = self.due_date

        notes = self.notes

        working_mem_ref_id = self.working_mem_ref_id

        habit_ref_id = self.habit_ref_id

        chore_ref_id = self.chore_ref_id

        big_plan_ref_id = self.big_plan_ref_id

        journal_ref_id = self.journal_ref_id

        metric_ref_id = self.metric_ref_id

        person_ref_id = self.person_ref_id

        slack_task_ref_id = self.slack_task_ref_id

        email_task_ref_id = self.email_task_ref_id

        recurring_timeline = self.recurring_timeline

        recurring_repeat_index = self.recurring_repeat_index

        recurring_gen_right_now = self.recurring_gen_right_now

        accepted_time = self.accepted_time

        working_time = self.working_time

        completed_time = self.completed_time

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
                "inbox_task_collection": inbox_task_collection,
                "source": source,
                "project_ref_id": project_ref_id,
                "status": status,
                "eisen": eisen,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if difficulty is not UNSET:
            field_dict["difficulty"] = difficulty
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date
        if due_date is not UNSET:
            field_dict["due_date"] = due_date
        if notes is not UNSET:
            field_dict["notes"] = notes
        if working_mem_ref_id is not UNSET:
            field_dict["working_mem_ref_id"] = working_mem_ref_id
        if habit_ref_id is not UNSET:
            field_dict["habit_ref_id"] = habit_ref_id
        if chore_ref_id is not UNSET:
            field_dict["chore_ref_id"] = chore_ref_id
        if big_plan_ref_id is not UNSET:
            field_dict["big_plan_ref_id"] = big_plan_ref_id
        if journal_ref_id is not UNSET:
            field_dict["journal_ref_id"] = journal_ref_id
        if metric_ref_id is not UNSET:
            field_dict["metric_ref_id"] = metric_ref_id
        if person_ref_id is not UNSET:
            field_dict["person_ref_id"] = person_ref_id
        if slack_task_ref_id is not UNSET:
            field_dict["slack_task_ref_id"] = slack_task_ref_id
        if email_task_ref_id is not UNSET:
            field_dict["email_task_ref_id"] = email_task_ref_id
        if recurring_timeline is not UNSET:
            field_dict["recurring_timeline"] = recurring_timeline
        if recurring_repeat_index is not UNSET:
            field_dict["recurring_repeat_index"] = recurring_repeat_index
        if recurring_gen_right_now is not UNSET:
            field_dict["recurring_gen_right_now"] = recurring_gen_right_now
        if accepted_time is not UNSET:
            field_dict["accepted_time"] = accepted_time
        if working_time is not UNSET:
            field_dict["working_time"] = working_time
        if completed_time is not UNSET:
            field_dict["completed_time"] = completed_time

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

        inbox_task_collection = d.pop("inbox_task_collection")

        source = InboxTaskSource(d.pop("source"))

        project_ref_id = d.pop("project_ref_id")

        status = InboxTaskStatus(d.pop("status"))

        eisen = Eisen(d.pop("eisen"))

        archived_time = d.pop("archived_time", UNSET)

        _difficulty = d.pop("difficulty", UNSET)
        difficulty: Union[Unset, Difficulty]
        if isinstance(_difficulty, Unset):
            difficulty = UNSET
        else:
            difficulty = Difficulty(_difficulty)

        actionable_date = d.pop("actionable_date", UNSET)

        due_date = d.pop("due_date", UNSET)

        notes = d.pop("notes", UNSET)

        working_mem_ref_id = d.pop("working_mem_ref_id", UNSET)

        habit_ref_id = d.pop("habit_ref_id", UNSET)

        chore_ref_id = d.pop("chore_ref_id", UNSET)

        big_plan_ref_id = d.pop("big_plan_ref_id", UNSET)

        journal_ref_id = d.pop("journal_ref_id", UNSET)

        metric_ref_id = d.pop("metric_ref_id", UNSET)

        person_ref_id = d.pop("person_ref_id", UNSET)

        slack_task_ref_id = d.pop("slack_task_ref_id", UNSET)

        email_task_ref_id = d.pop("email_task_ref_id", UNSET)

        recurring_timeline = d.pop("recurring_timeline", UNSET)

        recurring_repeat_index = d.pop("recurring_repeat_index", UNSET)

        recurring_gen_right_now = d.pop("recurring_gen_right_now", UNSET)

        accepted_time = d.pop("accepted_time", UNSET)

        working_time = d.pop("working_time", UNSET)

        completed_time = d.pop("completed_time", UNSET)

        inbox_task = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            inbox_task_collection=inbox_task_collection,
            source=source,
            project_ref_id=project_ref_id,
            status=status,
            eisen=eisen,
            archived_time=archived_time,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            notes=notes,
            working_mem_ref_id=working_mem_ref_id,
            habit_ref_id=habit_ref_id,
            chore_ref_id=chore_ref_id,
            big_plan_ref_id=big_plan_ref_id,
            journal_ref_id=journal_ref_id,
            metric_ref_id=metric_ref_id,
            person_ref_id=person_ref_id,
            slack_task_ref_id=slack_task_ref_id,
            email_task_ref_id=email_task_ref_id,
            recurring_timeline=recurring_timeline,
            recurring_repeat_index=recurring_repeat_index,
            recurring_gen_right_now=recurring_gen_right_now,
            accepted_time=accepted_time,
            working_time=working_time,
            completed_time=completed_time,
        )

        inbox_task.additional_properties = d
        return inbox_task

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
