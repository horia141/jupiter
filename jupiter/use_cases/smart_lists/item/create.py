"""The command for creating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.url import URL
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class SmartListItemCreateUseCase(UseCase['SmartListItemCreateUseCase.Args', None]):
    """The command for creating a smart list item."""

    @dataclass()
    class Args:
        """Args."""
        smart_list_key: SmartListKey
        name: SmartListItemName
        is_done: bool
        tag_names: List[SmartListTagName]
        url: Optional[URL]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.load_by_key(args.smart_list_key)
            smart_list_tags = \
                {t.tag_name: t
                 for t in uow.smart_list_tag_repository.find_all_for_smart_list(
                     smart_list_ref_id=smart_list.ref_id, filter_tag_names=args.tag_names)}
            for tag_name in args.tag_names:
                if tag_name in smart_list_tags:
                    continue
                smart_list_tag = SmartListTag.new_smart_list_tag(
                    smart_list_ref_id=smart_list.ref_id, tag_name=tag_name, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
                smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
                smart_list_tags[smart_list_tag.tag_name] = smart_list_tag
            smart_list_item = SmartListItem.new_smart_list_item(
                archived=False, smart_list_ref_id=smart_list.ref_id, name=args.name, is_done=args.is_done,
                tags_ref_id=[t.ref_id for t in smart_list_tags.values()], url=args.url, source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())
            smart_list_item = uow.smart_list_item_repository.create(smart_list_item)
        for smart_list_tag in smart_list_tags.values():
            notion_smart_list_tag = NotionSmartListTag.new_notion_row(smart_list_tag, None)
            self._smart_list_notion_manager.upsert_smart_list_tag(smart_list.ref_id, notion_smart_list_tag)
        notion_smart_list_item = \
            NotionSmartListItem.new_notion_row(
                smart_list_item,
                NotionSmartListItem.DirectExtraInfo({t.ref_id: t for t in smart_list_tags.values()}))
        self._smart_list_notion_manager.upsert_smart_list_item(smart_list.ref_id, notion_smart_list_item)
