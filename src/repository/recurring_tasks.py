"""Repository for recurring tasks."""
from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

import pendulum

from domain.common.entity_name import EntityName
from domain.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.common.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.common.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.common.recurring_task_skip_rule import RecurringTaskSkipRule
from domain.common.adate import ADate
from domain.common.recurring_task_period import RecurringTaskPeriod
from domain.common.recurring_task_type import RecurringTaskType
from domain.common.difficulty import Difficulty
from domain.common.eisen import Eisen
from models.framework import EntityId, JSONDictType
from utils.storage import BaseEntityRow, EntitiesStorage, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class RecurringTaskRow(BaseEntityRow):
    """A recurring task."""

    project_ref_id: EntityId
    name: EntityName
    period: RecurringTaskPeriod
    the_type: RecurringTaskType
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[RecurringTaskDueAtDay]
    actionable_from_month: Optional[RecurringTaskDueAtMonth]
    due_at_time: Optional[RecurringTaskDueAtTime]
    due_at_day: Optional[RecurringTaskDueAtDay]
    due_at_month: Optional[RecurringTaskDueAtMonth]
    suspended: bool
    skip_rule: Optional[RecurringTaskSkipRule]
    must_do: bool
    start_at_date: ADate
    end_at_date: Optional[ADate]


@typing.final
class RecurringTasksRepository:
    """A repository for recurring tasks."""

    _RECURRING_TASKS_FILE_PATH: ClassVar[Path] = Path("./recurring-tasks")
    _RECURRINg_TASKS_NUM_SHARDS: ClassVar[int] = 10

    _time_provider: Final[TimeProvider]
    _storage: Final[EntitiesStorage[RecurringTaskRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[RecurringTaskRow](
            self._RECURRING_TASKS_FILE_PATH, self._RECURRINg_TASKS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'RecurringTasksRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_recurring_task(
            self, project_ref_id: EntityId, archived: bool, name: EntityName, period: RecurringTaskPeriod,
            the_type: RecurringTaskType, eisen: Iterable[Eisen], difficulty: Optional[Difficulty],
            actionable_from_day: Optional[RecurringTaskDueAtDay],
            actionable_from_month: Optional[RecurringTaskDueAtMonth], due_at_time: Optional[RecurringTaskDueAtTime],
            due_at_day: Optional[RecurringTaskDueAtDay], due_at_month: Optional[RecurringTaskDueAtMonth],
            suspended: bool, skip_rule: Optional[RecurringTaskSkipRule], must_do: bool, start_at_date: ADate,
            end_at_date: Optional[ADate]) -> RecurringTaskRow:
        """Create a recurring task."""
        new_recurring_task_row = RecurringTaskRow(
            project_ref_id=project_ref_id,
            archived=archived,
            name=name,
            period=period,
            the_type=the_type,
            eisen=list(eisen),
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            suspended=suspended,
            skip_rule=skip_rule,
            must_do=must_do,
            start_at_date=start_at_date,
            end_at_date=end_at_date)

        return self._storage.create(new_recurring_task_row)

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTaskRow:
        """Remove a particular recurring task."""
        return self._storage.archive(ref_id)

    def remove_recurring_task(self, ref_id: EntityId) -> RecurringTaskRow:
        """Hard remove an inbox task."""
        return self._storage.remove(ref_id)

    def update_recurring_task(
            self, new_recurring_task: RecurringTaskRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> RecurringTaskRow:
        """Store a particular recurring task with all new properties."""
        return self._storage.update(new_recurring_task, archived_time_action)

    def load_recurring_task(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTaskRow:
        """Retrieve a particular recurring task by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_recurring_tasks(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTaskRow]:
        """Retrieve all the recurring tasks defined."""
        return self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            project_ref_id=In(*filter_project_ref_ids) if filter_project_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "project_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "period": {"type": "string"},
            "the_type": {"type": "string"},
            "eisen": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "difficulty": {"type": ["string", "null"]},
            "actionable_from_day": {"type": ["number", "null"]},
            "actionable_from_month": {"type": ["number", "null"]},
            "due_at_time": {"type": ["string", "null"]},
            "due_at_day": {"type": ["number", "null"]},
            "due_at_month": {"type": ["number", "null"]},
            "suspended": {"type": "boolean"},
            "skip_rule": {"type": ["string", "null"]},
            "must_do": {"type": "boolean"},
            "start_at_date": {"type": ["string", "null"]},
            "end_at_date": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> RecurringTaskRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        today_hack = pendulum.today().date()
        return RecurringTaskRow(
            project_ref_id=EntityId(typing.cast(str, storage_form["project_ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=EntityName.from_raw(typing.cast(str, storage_form["name"])),
            period=RecurringTaskPeriod(typing.cast(str, storage_form["period"])),
            the_type=RecurringTaskType(typing.cast(str, storage_form["the_type"])),
            eisen=[Eisen(e) for e in typing.cast(List[str], storage_form["eisen"])],
            difficulty=Difficulty(typing.cast(str, storage_form["difficulty"])) if storage_form["difficulty"] else None,
            actionable_from_day=RecurringTaskDueAtDay(typing.cast(int, storage_form["actionable_from_day"]))
            if storage_form.get("actionable_from_day", None) else None,
            actionable_from_month=RecurringTaskDueAtMonth(typing.cast(int, storage_form["actionable_from_month"]))
            if storage_form.get("actionable_from_month", None) else None,
            due_at_time=RecurringTaskDueAtTime(typing.cast(str, storage_form["due_at_time"]))
            if storage_form["due_at_time"] else None,
            due_at_day=RecurringTaskDueAtDay(typing.cast(int, storage_form["due_at_day"]))
            if storage_form["due_at_day"] else None,
            due_at_month=RecurringTaskDueAtMonth(typing.cast(int, storage_form["due_at_month"]))
            if storage_form["due_at_month"] else None,
            suspended=typing.cast(bool, storage_form["suspended"]),
            skip_rule=RecurringTaskSkipRule.from_raw(typing.cast(str, storage_form["skip_rule"]))
            if storage_form["skip_rule"] else None,
            must_do=typing.cast(bool, storage_form["must_do"]),
            start_at_date=ADate.from_str(typing.cast(str, storage_form["start_at_date"]))
            if storage_form["start_at_date"] else today_hack,
            end_at_date=ADate.from_str(typing.cast(str, storage_form["end_at_date"]))
            if storage_form["end_at_date"] else None)

    @staticmethod
    def live_to_storage(live_form: RecurringTaskRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "project_ref_id": str(live_form.project_ref_id),
            "name": str(live_form.name),
            "period": live_form.period.value,
            "the_type": live_form.the_type.value,
            "eisen": [e.value for e in live_form.eisen],
            "difficulty": live_form.difficulty.value if live_form.difficulty else None,
            "actionable_from_day": live_form.actionable_from_day.as_int() if live_form.actionable_from_day else None,
            "actionable_from_month":
                live_form.actionable_from_month.as_int() if live_form.actionable_from_month else None,
            "due_at_time": str(live_form.due_at_time) if live_form.due_at_time else None,
            "due_at_day": live_form.due_at_day.as_int() if live_form.due_at_day else None,
            "due_at_month": live_form.due_at_month.as_int() if live_form.due_at_month else None,
            "suspended": live_form.suspended,
            "skip_rule": str(live_form.skip_rule),
            "must_do": live_form.must_do,
            "start_at_date": str(live_form.start_at_date),
            "end_at_date": str(live_form.end_at_date) if live_form.end_at_date else None
        }
