"""The command for archiving a big plan."""
from dataclasses import dataclass

from jupiter.core.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class BigPlanArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class BigPlanArchiveUseCase(AppLoggedInMutationUseCase[BigPlanArchiveArgs, None]):
    """The command for archiving a big plan."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            big_plan = await uow.big_plan_repository.load_by_id(args.ref_id)

        await BigPlanArchiveService(
            EventSource.CLI, self._time_provider, self._storage_engine
        ).do_it(progress_reporter, big_plan)
