"""The command for removing a vacation entry."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.service.remove_service import VacationRemoveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class VacationRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class VacationRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[VacationRemoveArgs, None]
):
    """The command for removing a vacation."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.VACATIONS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        vacation = await uow.vacation_repository.load_by_id(
            args.ref_id,
            allow_archived=True,
        )
        vacation_remove_service = VacationRemoveService()
        await vacation_remove_service.do_it(uow, progress_reporter, vacation)
