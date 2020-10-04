"""The controller for vacations."""
from typing import Final, Iterable

from controllers.common import ControllerInputValidationError
from models.basic import EntityId, ADate
from repository.vacations import VacationRow
from service.vacations import VacationsService


class VacationsController:
    """The controller for vacations."""

    _vacations_service: Final[VacationsService]

    def __init__(self, vacations_service: VacationsService) -> None:
        """Constructor."""
        self._vacations_service = vacations_service

    def create_vacation(self, name: str, start_date: ADate, end_date: ADate) -> VacationRow:
        """Create a vacation."""
        return self._vacations_service.create_vacation(name, start_date, end_date)

    def archive_vacation(self, ref_id: EntityId) -> VacationRow:
        """Archive a vacation."""
        return self._vacations_service.archive_vacation(ref_id)

    def set_vacation_name(self, ref_id: EntityId, name: str) -> VacationRow:
        """Change the vacation name."""
        return self._vacations_service.set_vacation_name(ref_id, name)

    def set_vacation_start_date(self, ref_id: EntityId, start_date: ADate) -> VacationRow:
        """Change the vacation start date."""
        return self._vacations_service.set_vacation_start_date(ref_id, start_date)

    def set_vacation_end_date(self, ref_id: EntityId, end_date: ADate) -> VacationRow:
        """Change the vacation end date."""
        return self._vacations_service.set_vacation_end_date(ref_id, end_date)

    def load_all_vacations(self, allow_archived: bool = False) -> Iterable[VacationRow]:
        """Retrieve all vacations."""
        return self._vacations_service.load_all_vacations(allow_archived=allow_archived)

    def hard_remove_vacations(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove a vacation."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")
        for ref_id in ref_ids:
            self._vacations_service.hard_remove_vacation(ref_id)
