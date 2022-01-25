"""The command for finding vacations."""
from dataclasses import dataclass
from typing import Optional, List

from jupiter.domain.vacations.vacation import Vacation
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class VacationFindUseCase(AppReadonlyUseCase['VacationFindUseCase.Args', 'VacationFindUseCase.Result']):
    """The command for finding vacations."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        allow_archived: bool
        filter_ref_ids: Optional[List[EntityId]]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result object."""
        vacations: List[Vacation]

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'Result':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            vacations = uow.vacation_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids)
        return self.Result(vacations=vacations)
