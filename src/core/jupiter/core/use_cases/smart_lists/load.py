"""Use case for loading a smart list."""
from typing import List

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class SmartListLoadArgs(UseCaseArgsBase):
    """SmartListLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class SmartListLoadResult(UseCaseResultBase):
    """SmartListLoadResult."""

    smart_list: SmartList
    smart_list_tags: List[SmartListTag]
    smart_list_items: List[SmartListItem]


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SmartListLoadArgs, SmartListLoadResult]
):
    """Use case for loading a smart list."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListLoadArgs,
    ) -> SmartListLoadResult:
        """Execute the command's action."""
        smart_list = await uow.repository_for(SmartList).load_by_id(
            args.ref_id,
            allow_archived=args.allow_archived,
        )
        smart_list_tags = await uow.repository_for(SmartListTag).find_all_generic(
            parent_ref_id=smart_list.ref_id, allow_archived=args.allow_archived
        )
        smart_list_items = await uow.repository_for(SmartListItem).find_all_generic(
            parent_ref_id=smart_list.ref_id, allow_archived=args.allow_archived
        )

        return SmartListLoadResult(
            smart_list=smart_list,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
        )
