"""The command for finding smart lists."""
import itertools
from dataclasses import dataclass
from typing import Optional, Iterable

from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class SmartListFindUseCase(
    AppReadonlyUseCase["SmartListFindUseCase.Args", "SmartListFindUseCase.Result"]
):
    """The command for finding smart lists."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        allow_archived: bool
        filter_keys: Optional[Iterable[SmartListKey]]
        filter_is_done: Optional[bool]
        filter_tag_names: Optional[Iterable[SmartListTagName]]

    @dataclass(frozen=True)
    class ResponseEntry:
        """A single entry in the LoadAllSmartListsResponse."""

        smart_list: SmartList
        smart_list_tags: Iterable[SmartListTag]
        smart_list_items: Iterable[SmartListItem]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result object."""

        smart_lists: Iterable["SmartListFindUseCase.ResponseEntry"]

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> "SmartListFindUseCase.Result":
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )

            smart_lists = uow.smart_list_repository.find_all(
                parent_ref_id=smart_list_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_keys=args.filter_keys,
            )
            smart_list_tags = itertools.chain(
                *(
                    uow.smart_list_tag_repository.find_all_with_filters(
                        parent_ref_id=sl.ref_id,
                        allow_archived=args.allow_archived,
                        filter_tag_names=args.filter_tag_names,
                    )
                    for sl in smart_lists
                )
            )
            smart_list_items = itertools.chain(
                *(
                    uow.smart_list_item_repository.find_all_with_filters(
                        parent_ref_id=sl.ref_id,
                        allow_archived=args.allow_archived,
                        filter_is_done=args.filter_is_done,
                        filter_tag_ref_ids=[t.ref_id for t in smart_list_tags]
                        if args.filter_tag_names
                        else None,
                    )
                    for sl in smart_lists
                )
            )

        smart_list_tags_by_smart_list_ref_ids = {}
        for smart_list_tag in smart_list_tags:
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
        smart_list_items_by_smart_list_ref_ids = {}
        for smart_list_item in smart_list_items:
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
        return SmartListFindUseCase.Result(
            smart_lists=[
                SmartListFindUseCase.ResponseEntry(
                    smart_list=sl,
                    smart_list_tags=smart_list_tags_by_smart_list_ref_ids.get(
                        sl.ref_id, []
                    ),
                    smart_list_items=smart_list_items_by_smart_list_ref_ids.get(
                        sl.ref_id, []
                    ),
                )
                for sl in smart_lists
            ]
        )
