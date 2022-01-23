"""The command for finding smart lists."""
from dataclasses import dataclass
from typing import Optional, Iterable, Final

from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import UseCase


class SmartListFindUseCase(UseCase['SmartListFindUseCase.Args', 'SmartListFindUseCase.Response']):
    """The command for finding smart lists."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_keys: Optional[Iterable[SmartListKey]]
        filter_is_done: Optional[bool]
        filter_tag_names: Optional[Iterable[SmartListTagName]]

    @dataclass()
    class ResponseEntry:
        """A single entry in the LoadAllSmartListsResponse."""

        smart_list: SmartList
        smart_list_tags: Iterable[SmartListTag]
        smart_list_items: Iterable[SmartListItem]

    @dataclass()
    class Response:
        """Response object."""

        smart_lists: Iterable['SmartListFindUseCase.ResponseEntry']

    _storage_engine: Final[DomainStorageEngine]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'SmartListFindUseCase.Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_lists = uow.smart_list_repository.find_all(
                allow_archived=args.allow_archived, filter_keys=args.filter_keys)
            smart_list_tags = uow.smart_list_tag_repository.find_all(
                allow_archived=args.allow_archived,
                filter_smart_list_ref_ids=[sl.ref_id for sl in smart_lists],
                filter_tag_names=args.filter_tag_names)
            smart_list_items = uow.smart_list_item_repository.find_all(
                allow_archived=args.allow_archived,
                filter_is_done=args.filter_is_done,
                filter_tag_ref_ids=[t.ref_id for t in smart_list_tags] if args.filter_tag_names else None,
                filter_smart_list_ref_ids=[sl.ref_id for sl in smart_lists])

        smart_list_tags_by_smart_list_ref_ids = {}
        for smart_list_tag in smart_list_tags:
            if smart_list_tag.smart_list_ref_id not in smart_list_tags_by_smart_list_ref_ids:
                smart_list_tags_by_smart_list_ref_ids[smart_list_tag.smart_list_ref_id] = [smart_list_tag]
            else:
                smart_list_tags_by_smart_list_ref_ids[smart_list_tag.smart_list_ref_id].append(smart_list_tag)
        smart_list_items_by_smart_list_ref_ids = {}
        for smart_list_item in smart_list_items:
            if smart_list_item.smart_list_ref_id not in smart_list_items_by_smart_list_ref_ids:
                smart_list_items_by_smart_list_ref_ids[smart_list_item.smart_list_ref_id] = [smart_list_item]
            else:
                smart_list_items_by_smart_list_ref_ids[smart_list_item.smart_list_ref_id].append(smart_list_item)
        return SmartListFindUseCase.Response(
            smart_lists=[SmartListFindUseCase.ResponseEntry(
                smart_list=sl,
                smart_list_tags=smart_list_tags_by_smart_list_ref_ids.get(sl.ref_id, []),
                smart_list_items=smart_list_items_by_smart_list_ref_ids.get(sl.ref_id, [])) for sl in smart_lists])
