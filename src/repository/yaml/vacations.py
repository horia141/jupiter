"""Repository for vacations."""
from contextlib import contextmanager
from dataclasses import dataclass
import logging
from pathlib import Path
from types import TracebackType
import typing
from typing import ClassVar, Iterable, Optional, Final

import pendulum

from domain.vacations.infra.vacation_engine import VacationUnitOfWork, VacationEngine
from domain.vacations.infra.vacation_repository import VacationRepository
from domain.vacations.vacation import Vacation
from models.basic import BasicValidator, EntityName
from models.framework import EntityId, JSONDictType
from utils.storage import BaseEntityRow, EntitiesStorage, In
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _VacationRow(BaseEntityRow):
    """A vacation."""
    name: EntityName
    start_date: pendulum.Date
    end_date: pendulum.Date


class YamlVacationRepository(VacationRepository):
    """A repository for vacations."""

    _VACATIONS_FILE_PATH: ClassVar[Path] = Path("./vacations")
    _VACATIONS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_VacationRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_VacationRow](
            self._VACATIONS_FILE_PATH, self._VACATIONS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlVacationRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, vacation: Vacation) -> Vacation:
        """Create a vacation."""
        new_vacation_row = _VacationRow(
            archived=vacation.archived,
            name=vacation.name,
            start_date=vacation.start_date,
            end_date=vacation.end_date)
        vacation.assign_ref_id(new_vacation_row.ref_id)
        return vacation

    def save(self, vacation: Vacation) -> Vacation:
        """Save a vacation - it should already exist."""
        vacation_row = self._entity_to_row(vacation)
        vacation_row = self._storage.update(vacation_row)
        return self._row_to_entity(vacation_row)

    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Vacation:
        """Find a vacation by id."""
        return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> typing.List[Vacation]:
        """Find all vacations matching some criteria."""
        return [self._row_to_entity(vr)
                for vr in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*(str(fi) for fi in filter_ref_ids)) if filter_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove a vacation - an irreversible operation."""
        self._storage.remove(ref_id=ref_id)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _VacationRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _VacationRow(
            archived=typing.cast(bool, storage_form["archived"]),
            name=EntityName(typing.cast(str, storage_form["name"])),
            start_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["start_date"])),
            end_date=BasicValidator.adate_from_str(typing.cast(str, storage_form["end_date"])))

    @staticmethod
    def live_to_storage(live_form: _VacationRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "start_date": BasicValidator.adate_to_str(live_form.start_date),
            "end_date": BasicValidator.adate_to_str(live_form.end_date)
        }

    @staticmethod
    def _entity_to_row(vacation: Vacation) -> _VacationRow:
        vacation_row = _VacationRow(
            archived=vacation.archived,
            name=vacation.name,
            start_date=vacation.start_date,
            end_date=vacation.end_date)
        vacation_row.ref_id = vacation.ref_id
        vacation_row.created_time = vacation.created_time
        vacation_row.archived_time = vacation.archived_time
        vacation_row.last_modified_time = vacation.last_modified_time
        return vacation_row

    @staticmethod
    def _row_to_entity(row: _VacationRow) -> Vacation:
        return Vacation(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _name=row.name,
            _start_date=row.start_date,
            _end_date=row.end_date)


class YamlVacationUnitOfWork(VacationUnitOfWork):
    """A Yaml text file specific vacation unit of work."""

    _vacation_repository: Final[YamlVacationRepository]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._vacation_repository = YamlVacationRepository(time_provider)

    def __enter__(self) -> 'YamlVacationUnitOfWork':
        """Enter context."""
        self._vacation_repository.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""
        return self._vacation_repository


class YamlVacationEngine(VacationEngine):
    """An Yaml text file specific vacation engine."""

    _time_provider: Final[TimeProvider]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[VacationUnitOfWork]:
        """Get the unit of work."""
        yield YamlVacationUnitOfWork(self._time_provider)
