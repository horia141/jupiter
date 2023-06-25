"""The command for finding vacations."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class VacationFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class VacationFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    vacations: List[Vacation]


class VacationFindUseCase(
    AppLoggedInReadonlyUseCase[VacationFindArgs, VacationFindResult]
):
    """The command for finding vacations."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: VacationFindArgs,
    ) -> VacationFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = (
                await uow.vacation_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            vacations = await uow.vacation_repository.find_all(
                parent_ref_id=vacation_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
            )
        return VacationFindResult(vacations=vacations)
