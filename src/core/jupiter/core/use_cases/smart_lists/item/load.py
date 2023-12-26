"""Use case for loading a smart list item."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class SmartListItemLoadArgs(UseCaseArgsBase):
    """SmartListItemLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class SmartListItemLoadResult(UseCaseResultBase):
    """SmartListItemLoadResult."""

    smart_list_item: SmartListItem
    smart_list_tags: list[SmartListTag]


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListItemLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        SmartListItemLoadArgs, SmartListItemLoadResult
    ]
):
    """Use case for loading a smart list item."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListItemLoadArgs,
    ) -> SmartListItemLoadResult:
        """Execute the command's action."""
        item, tags = await generic_loader(
            uow,
            SmartListItem,
            args.ref_id,
            SmartListItem.tags,
            allow_archived=args.allow_archived,
        )

        return SmartListItemLoadResult(smart_list_item=item, smart_list_tags=list(tags))
