"""Use case for loading a particular vacation."""
from dataclasses import dataclass

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
class VacationLoadArgs(UseCaseArgsBase):
    """VacationLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class VacationLoadResult(UseCaseResultBase):
    """VacationLoadResult."""

    vacation: Vacation


class VacationLoadUseCase(
    AppLoggedInReadonlyUseCase[VacationLoadArgs, VacationLoadResult]
):
    """Use case for loading a particular vacation."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: VacationLoadArgs,
    ) -> VacationLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            vacation = await uow.vacation_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )

        return VacationLoadResult(vacation=vacation)
