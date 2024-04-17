from typing import Any, Dict, List, Type, TypeVar, Union, cast

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
        inbox_task_collection_ref_id (str):
        source (InboxTaskSource): The origin of an inbox task.
        project_ref_id (str): A generic entity id.
        status (InboxTaskStatus): The status of an inbox task.
        eisen (Eisen): The Eisenhower status of a particular task.
        archived_time (Union[None, Unset, str]):
        difficulty (Union[Difficulty, None, Unset]):
        actionable_date (Union[None, Unset, str]):
        due_date (Union[None, Unset, str]):
        notes (Union[None, Unset, str]):
        working_mem_ref_id (Union[None, Unset, str]):
        habit_ref_id (Union[None, Unset, str]):
        chore_ref_id (Union[None, Unset, str]):
        big_plan_ref_id (Union[None, Unset, str]):
        journal_ref_id (Union[None, Unset, str]):
        metric_ref_id (Union[None, Unset, str]):
        person_ref_id (Union[None, Unset, str]):
        slack_task_ref_id (Union[None, Unset, str]):
        email_task_ref_id (Union[None, Unset, str]):
        recurring_timeline (Union[None, Unset, str]):
        recurring_repeat_index (Union[None, Unset, int]):
        recurring_gen_right_now (Union[None, Unset, str]):
        accepted_time (Union[None, Unset, str]):
        working_time (Union[None, Unset, str]):
        completed_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    inbox_task_collection_ref_id: str
    source: InboxTaskSource
    project_ref_id: str
    status: InboxTaskStatus
    eisen: Eisen
    archived_time: Union[None, Unset, str] = UNSET
    difficulty: Union[Difficulty, None, Unset] = UNSET
    actionable_date: Union[None, Unset, str] = UNSET
    due_date: Union[None, Unset, str] = UNSET
    notes: Union[None, Unset, str] = UNSET
    working_mem_ref_id: Union[None, Unset, str] = UNSET
    habit_ref_id: Union[None, Unset, str] = UNSET
    chore_ref_id: Union[None, Unset, str] = UNSET
    big_plan_ref_id: Union[None, Unset, str] = UNSET
    journal_ref_id: Union[None, Unset, str] = UNSET
    metric_ref_id: Union[None, Unset, str] = UNSET
    person_ref_id: Union[None, Unset, str] = UNSET
    slack_task_ref_id: Union[None, Unset, str] = UNSET
    email_task_ref_id: Union[None, Unset, str] = UNSET
    recurring_timeline: Union[None, Unset, str] = UNSET
    recurring_repeat_index: Union[None, Unset, int] = UNSET
    recurring_gen_right_now: Union[None, Unset, str] = UNSET
    accepted_time: Union[None, Unset, str] = UNSET
    working_time: Union[None, Unset, str] = UNSET
    completed_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        inbox_task_collection_ref_id = self.inbox_task_collection_ref_id

        source = self.source.value

        project_ref_id = self.project_ref_id

        status = self.status.value

        eisen = self.eisen.value

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        difficulty: Union[None, Unset, str]
        if isinstance(self.difficulty, Unset):
            difficulty = UNSET
        elif isinstance(self.difficulty, Difficulty):
            difficulty = self.difficulty.value
        else:
            difficulty = self.difficulty

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

        notes: Union[None, Unset, str]
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        working_mem_ref_id: Union[None, Unset, str]
        if isinstance(self.working_mem_ref_id, Unset):
            working_mem_ref_id = UNSET
        else:
            working_mem_ref_id = self.working_mem_ref_id

        habit_ref_id: Union[None, Unset, str]
        if isinstance(self.habit_ref_id, Unset):
            habit_ref_id = UNSET
        else:
            habit_ref_id = self.habit_ref_id

        chore_ref_id: Union[None, Unset, str]
        if isinstance(self.chore_ref_id, Unset):
            chore_ref_id = UNSET
        else:
            chore_ref_id = self.chore_ref_id

        big_plan_ref_id: Union[None, Unset, str]
        if isinstance(self.big_plan_ref_id, Unset):
            big_plan_ref_id = UNSET
        else:
            big_plan_ref_id = self.big_plan_ref_id

        journal_ref_id: Union[None, Unset, str]
        if isinstance(self.journal_ref_id, Unset):
            journal_ref_id = UNSET
        else:
            journal_ref_id = self.journal_ref_id

        metric_ref_id: Union[None, Unset, str]
        if isinstance(self.metric_ref_id, Unset):
            metric_ref_id = UNSET
        else:
            metric_ref_id = self.metric_ref_id

        person_ref_id: Union[None, Unset, str]
        if isinstance(self.person_ref_id, Unset):
            person_ref_id = UNSET
        else:
            person_ref_id = self.person_ref_id

        slack_task_ref_id: Union[None, Unset, str]
        if isinstance(self.slack_task_ref_id, Unset):
            slack_task_ref_id = UNSET
        else:
            slack_task_ref_id = self.slack_task_ref_id

        email_task_ref_id: Union[None, Unset, str]
        if isinstance(self.email_task_ref_id, Unset):
            email_task_ref_id = UNSET
        else:
            email_task_ref_id = self.email_task_ref_id

        recurring_timeline: Union[None, Unset, str]
        if isinstance(self.recurring_timeline, Unset):
            recurring_timeline = UNSET
        else:
            recurring_timeline = self.recurring_timeline

        recurring_repeat_index: Union[None, Unset, int]
        if isinstance(self.recurring_repeat_index, Unset):
            recurring_repeat_index = UNSET
        else:
            recurring_repeat_index = self.recurring_repeat_index

        recurring_gen_right_now: Union[None, Unset, str]
        if isinstance(self.recurring_gen_right_now, Unset):
            recurring_gen_right_now = UNSET
        else:
            recurring_gen_right_now = self.recurring_gen_right_now

        accepted_time: Union[None, Unset, str]
        if isinstance(self.accepted_time, Unset):
            accepted_time = UNSET
        else:
            accepted_time = self.accepted_time

        working_time: Union[None, Unset, str]
        if isinstance(self.working_time, Unset):
            working_time = UNSET
        else:
            working_time = self.working_time

        completed_time: Union[None, Unset, str]
        if isinstance(self.completed_time, Unset):
            completed_time = UNSET
        else:
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
                "inbox_task_collection_ref_id": inbox_task_collection_ref_id,
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

        inbox_task_collection_ref_id = d.pop("inbox_task_collection_ref_id")

        source = InboxTaskSource(d.pop("source"))

        project_ref_id = d.pop("project_ref_id")

        status = InboxTaskStatus(d.pop("status"))

        eisen = Eisen(d.pop("eisen"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_difficulty(data: object) -> Union[Difficulty, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                difficulty_type_0 = Difficulty(data)

                return difficulty_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Difficulty, None, Unset], data)

        difficulty = _parse_difficulty(d.pop("difficulty", UNSET))

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

        def _parse_notes(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_working_mem_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        working_mem_ref_id = _parse_working_mem_ref_id(d.pop("working_mem_ref_id", UNSET))

        def _parse_habit_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        habit_ref_id = _parse_habit_ref_id(d.pop("habit_ref_id", UNSET))

        def _parse_chore_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        chore_ref_id = _parse_chore_ref_id(d.pop("chore_ref_id", UNSET))

        def _parse_big_plan_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        big_plan_ref_id = _parse_big_plan_ref_id(d.pop("big_plan_ref_id", UNSET))

        def _parse_journal_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        journal_ref_id = _parse_journal_ref_id(d.pop("journal_ref_id", UNSET))

        def _parse_metric_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        metric_ref_id = _parse_metric_ref_id(d.pop("metric_ref_id", UNSET))

        def _parse_person_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        person_ref_id = _parse_person_ref_id(d.pop("person_ref_id", UNSET))

        def _parse_slack_task_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        slack_task_ref_id = _parse_slack_task_ref_id(d.pop("slack_task_ref_id", UNSET))

        def _parse_email_task_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email_task_ref_id = _parse_email_task_ref_id(d.pop("email_task_ref_id", UNSET))

        def _parse_recurring_timeline(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        recurring_timeline = _parse_recurring_timeline(d.pop("recurring_timeline", UNSET))

        def _parse_recurring_repeat_index(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        recurring_repeat_index = _parse_recurring_repeat_index(d.pop("recurring_repeat_index", UNSET))

        def _parse_recurring_gen_right_now(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        recurring_gen_right_now = _parse_recurring_gen_right_now(d.pop("recurring_gen_right_now", UNSET))

        def _parse_accepted_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        accepted_time = _parse_accepted_time(d.pop("accepted_time", UNSET))

        def _parse_working_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        working_time = _parse_working_time(d.pop("working_time", UNSET))

        def _parse_completed_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        completed_time = _parse_completed_time(d.pop("completed_time", UNSET))

        inbox_task = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            inbox_task_collection_ref_id=inbox_task_collection_ref_id,
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
