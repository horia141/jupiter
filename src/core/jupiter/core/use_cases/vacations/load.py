"""Use case for loading a particular vacation."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
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


@readonly_use_case(WorkspaceFeature.VACATIONS)
class VacationLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[VacationLoadArgs, VacationLoadResult]
):
    """Use case for loading a particular vacation."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: VacationLoadArgs,
    ) -> VacationLoadResult:
        """Execute the command's action."""
        vacation = await generic_loader(
            uow, Vacation, args.ref_id, allow_archived=args.allow_archived
        )

        return VacationLoadResult(vacation=vacation)
