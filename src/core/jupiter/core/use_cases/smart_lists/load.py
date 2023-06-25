"""Use case for loading a smart list."""
from dataclasses import dataclass
from typing import List

from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
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
    AppLoggedInReadonlyUseCase[SmartListLoadArgs, SmartListLoadResult]
):
    """Use case for loading a smart list."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: SmartListLoadArgs,
    ) -> SmartListLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            smart_list = await uow.smart_list_repository.load_by_id(
                args.ref_id,
                allow_archived=args.allow_archived,
            )
            smart_list_tags = await uow.smart_list_tag_repository.find_all_with_filters(
                smart_list.ref_id, allow_archived=args.allow_archived
            )
            smart_list_items = (
                await uow.smart_list_item_repository.find_all_with_filters(
                    smart_list.ref_id, allow_archived=args.allow_archived
                )
            )

        return SmartListLoadResult(
            smart_list=smart_list,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
        )
