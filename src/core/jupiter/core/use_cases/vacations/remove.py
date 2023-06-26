"""The command for removing a vacation entry."""
from dataclasses import dataclass

from jupiter.core.domain.vacations.service.remove_service import VacationRemoveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class VacationRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class VacationRemoveUseCase(AppLoggedInMutationUseCase[VacationRemoveArgs, None]):
    """The command for removing a vacation."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            vacation = await uow.vacation_repository.load_by_id(
                args.ref_id,
                allow_archived=True,
            )
        vacation_remove_service = VacationRemoveService(
            self._storage_engine,
        )
        await vacation_remove_service.do_it(progress_reporter, vacation)