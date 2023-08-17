"""The command for archiving a big plan."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class BigPlanArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class BigPlanArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanArchiveArgs, None]
):
    """The command for archiving a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.BIG_PLANS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        big_plan = await uow.big_plan_repository.load_by_id(args.ref_id)

        await BigPlanArchiveService(EventSource.CLI, self._time_provider).do_it(
            uow, progress_reporter, big_plan
        )
