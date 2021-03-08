"""Repository for vacations."""

from dataclasses import dataclass
import logging
from pathlib import Path
from types import TracebackType
import typing
from typing import ClassVar, Iterable, Optional, Final

import pendulum

from models.basic import EntityId, ADate, BasicValidator
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class VacationRow(BaseEntityRow):
    """A vacation."""

    name: str
    start_date: pendulum.Date
    end_date: pendulum.Date


class VacationsRepository:
    """A repository for vacations."""

    _VACATIONS_FILE_PATH: ClassVar[Path] = Path("./vacations")
    _VACATIONS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[VacationRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[VacationRow](
            self._VACATIONS_FILE_PATH, self._VACATIONS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'VacationsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_vacation(
            self, archived: bool, name: str, start_date: ADate, end_date: ADate) -> VacationRow:
        """Create a vacation."""
        new_vacation = VacationRow(
            archived=archived,
            name=name,
            start_date=start_date,
            end_date=end_date)
        return self._storage.create(new_vacation)

    def archive_vacation(self, ref_id: EntityId) -> VacationRow:
        """Remove a particular vacation."""
        return self._storage.archive(ref_id=ref_id)

    def remove_vacation(self, ref_id: EntityId) -> VacationRow:
        """Hard remove a vacation."""
        return self._storage.remove(ref_id=ref_id)

    def update_vacation(
            self, new_vacation: VacationRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> VacationRow:
        """Store a particular vacation with all new properties."""
        return self._storage.update(new_vacation, archived_time_action=archived_time_action)

    def load_vacation(self, ref_id: EntityId, allow_archived: bool = False) -> VacationRow:
        """Retrieve a particular vacation by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def load_all_vacations(
            self, allow_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[VacationRow]:
        """Retrieve all the vacations defined."""
        return self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> VacationRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return VacationRow(
            archived=typing.cast(bool, storage_form["archived"]),
            name=typing.cast(str, storage_form["name"]),
            start_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["start_date"])),
            end_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["end_date"])))

    @staticmethod
    def live_to_storage(live_form: VacationRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "start_date": BasicValidator.adate_to_str(live_form.start_date),
            "end_date": BasicValidator.adate_to_str(live_form.end_date)
        }
