"""Use case for loading a smart list."""
from dataclasses import dataclass
from typing import Iterable, List

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class SmartListLoadArgs(UseCaseArgsBase):
    """SmartListLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class SmartListLoadResult(UseCaseResultBase):
    """SmartListLoadResult."""

    smart_list: SmartList
    smart_list_tags: List[SmartListTag]
    smart_list_items: List[SmartListItem]


class SmartListLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SmartListLoadArgs, SmartListLoadResult]
):
    """Use case for loading a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: SmartListLoadArgs,
    ) -> SmartListLoadResult:
        """Execute the command's action."""
        smart_list = await uow.smart_list_repository.load_by_id(
            args.ref_id,
            allow_archived=args.allow_archived,
        )
        smart_list_tags = await uow.smart_list_tag_repository.find_all_with_filters(
            smart_list.ref_id, allow_archived=args.allow_archived
        )
        smart_list_items = await uow.smart_list_item_repository.find_all_with_filters(
            smart_list.ref_id, allow_archived=args.allow_archived
        )

        return SmartListLoadResult(
            smart_list=smart_list,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
        )
