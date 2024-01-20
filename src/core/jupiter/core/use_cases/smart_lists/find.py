"""The command for finding smart lists."""
from typing import List, Optional

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
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


@use_case_result_part
class SmartListFindResponseEntry:
    """A single entry in the LoadAllSmartListsResponse."""

    smart_list: SmartList
    smart_list_tags: Optional[List[SmartListTag]] = None
    smart_list_items: Optional[List[SmartListItem]] = None


@use_case_result
class SmartListFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    entries: List[SmartListFindResponseEntry]


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[SmartListFindArgs, SmartListFindResult]
):
    """The command for finding smart lists."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListFindArgs,
    ) -> SmartListFindResult:
        """Execute the command's action."""
        workspace = context.workspace

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
                        smart_list_tag.smart_list.ref_id
                        not in smart_list_tags_by_smart_list_ref_ids
                    ):
                        smart_list_tags_by_smart_list_ref_ids[
                            smart_list_tag.smart_list.ref_id
                        ] = [smart_list_tag]
                    else:
                        smart_list_tags_by_smart_list_ref_ids[
                            smart_list_tag.smart_list.ref_id
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
                        smart_list_item.smart_list.ref_id
                        not in smart_list_items_by_smart_list_ref_ids
                    ):
                        smart_list_items_by_smart_list_ref_ids[
                            smart_list_item.smart_list.ref_id
                        ] = [smart_list_item]
                    else:
                        smart_list_items_by_smart_list_ref_ids[
                            smart_list_item.smart_list.ref_id
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
