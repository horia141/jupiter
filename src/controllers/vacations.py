"""The controller for vacations."""
from typing import Final, Iterable

import pendulum

from controllers.common import ControllerInputValidationError
from models.basic import EntityId
from repository.vacations import Vacation
from service.vacations import VacationsService


class VacationsController:
    """The controller for vacations."""

    _vacations_service: Final[VacationsService]

    def __init__(self, vacations_service: VacationsService) -> None:
        """Constructor."""
        self._vacations_service = vacations_service

    def create_vacation(self, name: str, start_date: pendulum.DateTime, end_date: pendulum.DateTime) -> Vacation:
        """Create a vacation."""
        return self._vacations_service.create_vacation(name, start_date, end_date)

    def archive_vacation(self, ref_id: EntityId) -> Vacation:
        """Archive a vacation."""
        return self._vacations_service.archive_vacation(ref_id)

    def set_vacation_name(self, ref_id: EntityId, name: str) -> Vacation:
        """Change the vacation name."""
        return self._vacations_service.set_vacation_name(ref_id, name)

    def set_vacation_start_date(self, ref_id: EntityId, start_date: pendulum.DateTime) -> Vacation:
        """Change the vacation start date."""
        return self._vacations_service.set_vacation_start_date(ref_id, start_date)

    def set_vacation_end_date(self, ref_id: EntityId, end_date: pendulum.DateTime) -> Vacation:
        """Change the vacation end date."""
        return self._vacations_service.set_vacation_end_date(ref_id, end_date)

    def load_all_vacations(self, show_archived: bool = False) -> Iterable[Vacation]:
        """Retrieve all vacations."""
        return self._vacations_service.load_all_vacations(show_archived)

    def hard_remove_vacations(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove a vacation."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")
        for ref_id in ref_ids:
            self._vacations_service.hard_remove_vacation(ref_id)
