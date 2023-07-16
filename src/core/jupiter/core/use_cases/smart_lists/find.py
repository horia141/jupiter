"""The command for finding smart lists."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
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
class SmartListFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_tags: bool
    include_items: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_is_done: Optional[bool] = None
    filter_tag_names: Optional[List[SmartListTagName]] = None
    filter_tag_ref_id: Optional[List[EntityId]] = None
    filter_item_ref_id: Optional[List[EntityId]] = None


@dataclass
class SmartListFindResponseEntry:
    """A single entry in the LoadAllSmartListsResponse."""

    smart_list: SmartList
    smart_list_tags: Optional[List[SmartListTag]] = None
    smart_list_items: Optional[List[SmartListItem]] = None


@dataclass
class SmartListFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    entries: List[SmartListFindResponseEntry]


class SmartListFindUseCase(
    AppLoggedInReadonlyUseCase[SmartListFindArgs, SmartListFindResult]
):
    """The command for finding smart lists."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: SmartListFindArgs,
    ) -> SmartListFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            smart_lists = await uow.smart_list_repository.find_all(
                parent_ref_id=smart_list_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
            )

            if args.include_tags:
                smart_list_tags_by_smart_list_ref_ids = {}
                for smart_list in smart_lists:
                    for (
                        smart_list_tag
                    ) in await uow.smart_list_tag_repository.find_all_with_filters(
                        parent_ref_id=smart_list.ref_id,
                        allow_archived=args.allow_archived,
                        filter_tag_names=args.filter_tag_names,
                        filter_ref_ids=args.filter_tag_ref_id,
                    ):
                        if (
                            smart_list_tag.smart_list_ref_id
                            not in smart_list_tags_by_smart_list_ref_ids
                        ):
                            smart_list_tags_by_smart_list_ref_ids[
                                smart_list_tag.smart_list_ref_id
                            ] = [smart_list_tag]
                        else:
                            smart_list_tags_by_smart_list_ref_ids[
                                smart_list_tag.smart_list_ref_id
                            ].append(smart_list_tag)
            else:
                smart_list_tags_by_smart_list_ref_ids = None

            if args.include_items:
                smart_list_items_by_smart_list_ref_ids = {}
                for smart_list in smart_lists:
                    for (
                        smart_list_item
                    ) in await uow.smart_list_item_repository.find_all_with_filters(
                        parent_ref_id=smart_list.ref_id,
                        allow_archived=args.allow_archived,
                        filter_ref_ids=args.filter_item_ref_id,
                        filter_is_done=args.filter_is_done,
                        filter_tag_ref_ids=args.filter_tag_ref_id,
                    ):
                        if (
                            smart_list_item.smart_list_ref_id
                            not in smart_list_items_by_smart_list_ref_ids
                        ):
                            smart_list_items_by_smart_list_ref_ids[
                                smart_list_item.smart_list_ref_id
                            ] = [smart_list_item]
                        else:
                            smart_list_items_by_smart_list_ref_ids[
                                smart_list_item.smart_list_ref_id
                            ].append(smart_list_item)
            else:
                smart_list_items_by_smart_list_ref_ids = None

        return SmartListFindResult(
            entries=[
                SmartListFindResponseEntry(
                    smart_list=sl,
                    smart_list_tags=smart_list_tags_by_smart_list_ref_ids.get(
                        sl.ref_id,
                        [],
                    )
                    if smart_list_tags_by_smart_list_ref_ids is not None
                    else None,
                    smart_list_items=smart_list_items_by_smart_list_ref_ids.get(
                        sl.ref_id,
                        [],
                    )
                    if smart_list_items_by_smart_list_ref_ids is not None
                    else None,
                )
                for sl in smart_lists
            ],
        )
