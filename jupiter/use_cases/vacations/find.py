"""The command for finding vacations."""
from dataclasses import dataclass
from typing import Final, Optional, List

from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.vacations.vacation import Vacation
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase


class VacationFindUseCase(UseCase['VacationFindUseCase.Args', 'VacationFindUseCase.Response']):
    """The command for finding vacations."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_ref_ids: Optional[List[EntityId]]

    @dataclass()
    class Response:
        """Response object."""

        vacations: List[Vacation]

    _storage_engine: Final[StorageEngine]

    def __init__(self, storage_engine: StorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            vacations = uow.vacation_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids)
        return self.Response(vacations=vacations)
