"""Use case for loading a smart list item."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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
class SmartListItemLoadArgs(UseCaseArgsBase):
    """SmartListItemLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class SmartListItemLoadResult(UseCaseResultBase):
    """SmartListItemLoadResult."""

    smart_list_item: SmartListItem
    smart_list_tags: list[SmartListTag]


class SmartListItemLoadUseCase(
    AppLoggedInReadonlyUseCase[SmartListItemLoadArgs, SmartListItemLoadResult]
):
    """Use case for loading a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemLoadArgs,
    ) -> SmartListItemLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            smart_list_item = await uow.smart_list_item_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )
            smart_list_tags = await uow.smart_list_tag_repository.find_all_with_filters(
                smart_list_item.smart_list_ref_id,
                allow_archived=args.allow_archived,
            )

        return SmartListItemLoadResult(
            smart_list_item=smart_list_item, smart_list_tags=smart_list_tags
        )
