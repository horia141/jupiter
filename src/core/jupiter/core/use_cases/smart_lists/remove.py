"""The command for hard removing a smart list."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class SmartListRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListRemoveArgs, None]
):
    """The command for removing a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.smart_list_repository.load_by_id(
            args.ref_id, allow_archived=True
        )

        smart_list_remove_service = SmartListRemoveService()
        await smart_list_remove_service.execute(
            uow,
            progress_reporter,
            smart_list,
        )
