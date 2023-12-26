"""The command for removing a smart list item."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_remover import generic_remover
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class SmartListItemRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListItemRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListItemRemoveArgs, None]
):
    """The command for removing a smart list item."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListItemRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_remover(
            context.domain_context, uow, progress_reporter, SmartListItem, args.ref_id
        )
