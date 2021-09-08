"""The command for creating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from domain.common.url import URL
from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list_item import SmartListItem
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from domain.common.entity_name import EntityName
from domain.smart_lists.smart_list_key import SmartListKey
from models.framework import Command
from utils.time_provider import TimeProvider


class SmartListItemCreateCommand(Command['SmartListItemCreateCommand.Args', None]):
    """The command for creating a smart list item."""

    @dataclass()
    class Args:
        """Args."""
        smart_list_key: SmartListKey
        name: EntityName
        is_done: bool
        tag_names: List[SmartListTagName]
        url: Optional[URL]

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

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.get_by_key(args.smart_list_key)
            smart_list_tags = \
                {t.tag_name: t
                 for t in uow.smart_list_tag_repository.find_all_for_smart_list(
                     smart_list_ref_id=smart_list.ref_id, filter_tag_names=args.tag_names)}
            for tag_name in args.tag_names:
                if tag_name in smart_list_tags:
                    continue
                smart_list_tag = SmartListTag.new_smart_list_tag(
                    smart_list_ref_id=smart_list.ref_id, tag_name=tag_name,
                    created_time=self._time_provider.get_current_time())
                smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
                smart_list_tags[smart_list_tag.tag_name] = smart_list_tag
            smart_list_item = SmartListItem.new_smart_list_item(
                archived=False, smart_list_ref_id=smart_list.ref_id, name=args.name, is_done=args.is_done,
                tags_ref_id=[t.ref_id for t in smart_list_tags.values()], url=args.url,
                created_time=self._time_provider.get_current_time())
            smart_list_item = uow.smart_list_item_repository.create(smart_list_item)
        for smart_list_tag in smart_list_tags.values():
            self._notion_manager.upsert_smart_list_tag(smart_list_tag)
        self._notion_manager.upsert_smart_list_item(smart_list_item, smart_list_tags.keys())
