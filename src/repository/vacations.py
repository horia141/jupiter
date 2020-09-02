"""Repository for vacations."""

from dataclasses import dataclass
import logging
from pathlib import Path
from types import TracebackType
import typing
from typing import ClassVar, List, Iterable, Optional, Final

import pendulum
from pendulum import UTC

from models.basic import EntityId, ADate, BasicValidator, Timestamp
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@typing.final
@dataclass()
class Vacation:
    """A vacation."""

    ref_id: EntityId
    archived: bool
    name: str
    start_date: pendulum.Date
    end_date: pendulum.Date
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]

    def is_in_vacation(self, start_date: ADate, end_date: ADate) -> bool:
        """Checks whether a particular date range is in this vacation."""
        if isinstance(start_date, pendulum.DateTime):
            vacation_start_date = pendulum.DateTime(
                self.start_date.year, self.start_date.month, self.start_date.day, tzinfo=UTC)
        else:
            vacation_start_date = self.start_date
        if isinstance(end_date, pendulum.DateTime):
            vacation_end_date = pendulum.DateTime(
                self.end_date.year, self.end_date.month, self.end_date.day, tzinfo=UTC).end_of("day")
        else:
            vacation_end_date = self.end_date
        return typing.cast(bool, vacation_start_date <= start_date) and \
               typing.cast(bool, end_date <= vacation_end_date)


@typing.final
class VacationsRepository:
    """A repository for vacations."""

    _VACATIONS_FILE_PATH: ClassVar[Path] = Path("/data/vacations.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[Vacation]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._VACATIONS_FILE_PATH, self)

    def __enter__(self) -> 'VacationsRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_vacation(
            self, archived: bool, name: str, start_date: ADate, end_date: ADate) -> Vacation:
        """Create a vacation."""
        vacations_next_idx, vacations = self._structured_storage.load()

        new_vacation = Vacation(
            ref_id=EntityId(str(vacations_next_idx)),
            archived=archived,
            name=name,
            start_date=start_date,
            end_date=end_date,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None)
        vacations_next_idx += 1
        vacations.append(new_vacation)
        vacations.sort(key=lambda v: v.start_date)

        self._structured_storage.save((vacations_next_idx, vacations))

        return new_vacation

    def archive_vacation(self, ref_id: EntityId) -> Vacation:
        """Remove a particular vacation."""
        vacations_next_idx, vacations = self._structured_storage.load()

        for vacation in vacations:
            if vacation.ref_id == ref_id:
                vacation.archived = True
                vacation.last_modified_time = self._time_provider.get_current_time()
                vacation.archived_time = self._time_provider.get_current_time()
                self._structured_storage.save((vacations_next_idx, vacations))
                return vacation

        raise RepositoryError(f"Vacation with id='{ref_id}' does not exist")

    def load_all_vacations(
            self, filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[Vacation]:
        """Retrieve all the vacations defined."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        _, vacations = self._structured_storage.load()
        return [v for v in vacations
                if (filter_archived is False or v.archived is False)
                and (len(filter_ref_ids_set) == 0 or v.ref_id in filter_ref_ids_set)]

    def load_vacation(self, ref_id: EntityId, allow_archived: bool = False) -> Vacation:
        """Retrieve a particular vacation by its id."""
        _, vacations = self._structured_storage.load()
        found_vacation = self._find_vacation_by_id(ref_id, vacations)
        if not found_vacation:
            raise RepositoryError(f"Vacation with id={ref_id} does not exist")
        if not allow_archived and found_vacation.archived:
            raise RepositoryError(f"Vacation with id={ref_id} is archived")
        return found_vacation

    def save_vacation(
            self, new_vacation: Vacation,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> Vacation:
        """Store a particular vacation with all new properties."""
        vacations_next_idx, vacations = self._structured_storage.load()
        if not self._find_vacation_by_id(new_vacation.ref_id, vacations):
            raise RepositoryError(f"Vacation with id={new_vacation.ref_id} does not exist")
        new_vacation.last_modified_time = self._time_provider.get_current_time()
        archived_time_action.act(new_vacation, "archived_time", self._time_provider.get_current_time())
        new_vacations = [(v if v.ref_id != new_vacation.ref_id else new_vacation) for v in vacations]
        self._structured_storage.save((vacations_next_idx, new_vacations))

        return new_vacation

    def hard_remove_vacation(self, ref_id: EntityId) -> Vacation:
        """Hard remove a vacation."""
        vacations_next_idx, vacations = self._structured_storage.load()
        found_vacations = self._find_vacation_by_id(ref_id, vacations)
        if not found_vacations:
            raise RepositoryError(f"Vacation with id='{ref_id}' does not exist")
        new_vacations = [it for it in vacations if it.ref_id != ref_id]
        self._structured_storage.save((vacations_next_idx, new_vacations))
        return found_vacations

    @staticmethod
    def _find_vacation_by_id(ref_id: EntityId, vacations: List[Vacation]) -> Optional[Vacation]:
        try:
            return next(v for v in vacations if v.ref_id == ref_id)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "archived": {"type": "boolean"},
                "name": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> Vacation:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Vacation(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=typing.cast(str, storage_form["name"]),
            start_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["start_date"])),
            end_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["end_date"])),
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] is not None else None)

    @staticmethod
    def live_to_storage(live_form: Vacation) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "archived": live_form.archived,
            "name": live_form.name,
            "start_date": BasicValidator.adate_to_str(live_form.start_date),
            "end_date": BasicValidator.adate_to_str(live_form.end_date),
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time),
            "archived_time": BasicValidator.timestamp_to_str(live_form.archived_time)
                             if live_form.archived_time else None
        }
