"""The command for removing a smart list item."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import WorkspaceFeature
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
class SmartListItemRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListItemRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListItemRemoveArgs, None]
):
    """The command for removing a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_item = await uow.smart_list_item_repository.remove(
            args.ref_id,
        )
        await progress_reporter.mark_removed(smart_list_item)
