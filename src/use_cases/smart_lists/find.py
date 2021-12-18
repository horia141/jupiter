"""The command for finding smart lists."""
from dataclasses import dataclass
from typing import Optional, Iterable, Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list import SmartList
from domain.smart_lists.smart_list_item import SmartListItem
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from domain.smart_lists.smart_list_key import SmartListKey
from models.framework import Command
from utils.time_provider import TimeProvider


class SmartListFindCommand(Command['SmartListFindCommand.Args', 'SmartListFindCommand.Response']):
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

        smart_lists: Iterable['SmartListFindCommand.ResponseEntry']

    _time_provider: Final[TimeProvider]
    _smart_list_engine: Final[SmartListEngine]
    _notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, smart_list_engine: SmartListEngine,
            notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._smart_list_engine = smart_list_engine
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> 'SmartListFindCommand.Response':
        """Execute the command's action."""
        with self._smart_list_engine.get_unit_of_work() as uow:
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
        return SmartListFindCommand.Response(
            smart_lists=[SmartListFindCommand.ResponseEntry(
                smart_list=sl,
                smart_list_tags=smart_list_tags_by_smart_list_ref_ids.get(sl.ref_id, []),
                smart_list_items=smart_list_items_by_smart_list_ref_ids.get(sl.ref_id, [])) for sl in smart_lists])
