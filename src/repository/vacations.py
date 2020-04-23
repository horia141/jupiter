"""Repository for vacations."""

import datetime
import logging
import os.path
import typing
from typing import Final, Any, ClassVar, Dict, List, Optional, Sequence, Tuple

import jsonschema as js
import yaml

from repository.common import RefId, RepositoryError

LOGGER = logging.getLogger(__name__)


class Vacation:
    """A vacation."""

    _ref_id: RefId
    _archived: bool
    _name: str
    _start_date: datetime.date
    _end_date: datetime.date

    def __init__(
            self, ref_id: RefId, archived: bool, name: str, start_date: datetime.date,
            end_date: datetime.date) -> None:
        """Constructor."""
        self._ref_id = ref_id
        self._archived = archived
        self._name = name
        self._start_date = start_date
        self._end_date = end_date

    def set_archived(self, archived: bool) -> None:
        """Set the archived status of a vacation."""
        self._archived = archived

    def set_name(self, name: str) -> None:
        """Set the name of a vacation."""
        self._name = name

    def set_start_date(self, start_date: datetime.date) -> None:
        """Set the start date of a vacation."""
        self._start_date = start_date

    def set_end_date(self, end_date: datetime.date) -> None:
        """Set the end date of a vacation."""
        self._end_date = end_date

    @property
    def ref_id(self) -> RefId:
        """The unique id of the vacation."""
        return self._ref_id

    @property
    def archived(self) -> bool:
        """The archived status of the vacation."""
        return self._archived

    @property
    def name(self) -> str:
        """The name of the vacation."""
        return self._name

    @property
    def start_date(self) -> datetime.date:
        """The start date of the vacation."""
        return self._start_date

    @property
    def end_date(self) -> datetime.date:
        """The end date of the vacation."""
        return self._end_date


@typing.final
class VacationsRepository:
    """A repository for vacations."""

    _VACATIONS_FILE_PATH: Final[ClassVar[str]] = "/data/vacations.yaml"

    _VACATIONS_SCHEMA: Final[ClassVar[Dict[str, Any]]] = {
        "type": "object",
        "properties": {
            "next_idx": {"type": "number"},
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ref_id": {"type": "string"},
                        "archived": {"type": "boolean"},
                        "name": {"type": "string"},
                        "start_date": {"type": "datetime-date"},
                        "end_date": {"type": "datetime-date"}
                    }
                }
            }
        }
    }

    _validator: Final[Any]

    def __init__(self) -> None:
        """Constructor."""
        custom_type_checker = js.Draft6Validator.TYPE_CHECKER \
            .redefine("datetime-date", VacationsRepository._schema_check_datetime_date)

        self._validator = js.validators.extend(js.Draft6Validator, type_checker=custom_type_checker)

    def initialize(self) -> None:
        """Initialise this repository."""
        if os.path.exists(VacationsRepository._VACATIONS_FILE_PATH):
            return
        self._bulk_save_vacations((0, []))

    def create_vacation(
            self, archived: bool, name: str, start_date: datetime.date, end_date: datetime.date) -> Vacation:
        """Create a vacation."""
        vacations_next_idx, vacations = self._bulk_load_vacations()

        new_vacation = Vacation(
            ref_id=RefId(str(vacations_next_idx)),
            archived=archived,
            name=name,
            start_date=start_date,
            end_date=end_date)
        vacations_next_idx += 1
        vacations.append(new_vacation)
        vacations.sort(key=lambda v: v.start_date)

        self._bulk_save_vacations((vacations_next_idx, vacations))

        return new_vacation

    def remove_vacation_by_id(self, ref_id: RefId) -> None:
        """Remove a particular vacation."""
        vacations_next_idx, vacations = self._bulk_load_vacations()

        for vacation in vacations:
            if vacation.ref_id == ref_id:
                vacation.set_archived(True)
                break
        else:
            raise RepositoryError(f"Vacation with id='{ref_id}' does not exist")

        self._bulk_save_vacations((vacations_next_idx, vacations))

    def load_all_vacations(self) -> Sequence[Vacation]:
        """Retrieve all the vacations defined."""
        _, vacations = self._bulk_load_vacations()
        return vacations

    def load_vacation_by_id(self, ref_id: RefId) -> Vacation:
        """Retrieve a particular vacation by its id."""
        _, vacations = self._bulk_load_vacations()
        found_vacation = self._find_vacation_by_id(ref_id, vacations)
        if not found_vacation:
            raise RepositoryError(f"Vacation with id={ref_id} does not exist")
        return found_vacation

    def save_vacation(self, new_vacation: Vacation) -> None:
        """Store a particular vacation with all new properties."""
        vacations_next_idx, vacations = self._bulk_load_vacations()
        if not self._find_vacation_by_id(new_vacation.ref_id, vacations):
            raise RepositoryError(f"Vacation with id={new_vacation.ref_id} does not exist")
        new_vacations = [(v if v.ref_id != new_vacation.ref_id else new_vacation) for v in vacations]
        self._bulk_save_vacations((vacations_next_idx, new_vacations))

    def _bulk_load_vacations(self) -> Tuple[int, List[Vacation]]:
        try:
            with open(VacationsRepository._VACATIONS_FILE_PATH, "r") as vacations_file:
                vacations_ser = yaml.safe_load(vacations_file)
                LOGGER.info("Loaded vacations data")

                self._validator(VacationsRepository._VACATIONS_SCHEMA).validate(vacations_ser)
                LOGGER.info("Checked vacations structure")

                vacations_next_idx = vacations_ser["next_idx"]
                all_vacations = \
                    (Vacation(
                        ref_id=RefId(v["ref_id"]),
                        archived=v["archived"],
                        name=v["name"],
                        start_date=v["start_date"],
                        end_date=v["end_date"])
                     for v in vacations_ser["entries"])
                vacations = [v for v in all_vacations
                             if v.archived is False]

                return vacations_next_idx, vacations
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def _bulk_save_vacations(self, bulk_data: Tuple[int, Sequence[Vacation]]) -> None:
        try:
            with open(VacationsRepository._VACATIONS_FILE_PATH, "w") as vacations_file:
                vacations_ser = {
                    "next_idx": bulk_data[0],
                    "entries": [{
                        "ref_id": v.ref_id,
                        "archived": v.archived,
                        "name": v.name,
                        "start_date": v.start_date,
                        "end_date": v.end_date
                    } for v in bulk_data[1]]
                }

                self._validator(VacationsRepository._VACATIONS_SCHEMA).validate(vacations_ser)
                LOGGER.info("Checked vacations structure")

                yaml.dump(vacations_ser, vacations_file)
                LOGGER.info("Saved vacations structure")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    @staticmethod
    def _schema_check_datetime_date(_checker: Any, instance: Any) -> bool:
        return isinstance(instance, datetime.date)

    @staticmethod
    def _find_vacation_by_id(ref_id: RefId, vacations: Sequence[Vacation]) -> Optional[Vacation]:
        try:
            return next(v for v in vacations if v.key == ref_id)
        except StopIteration:
            return None
