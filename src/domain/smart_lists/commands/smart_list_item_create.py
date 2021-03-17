"""The command for creating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list_item import SmartListItem
from domain.smart_lists.smart_list_tag import SmartListTag
from models.basic import SmartListKey, EntityName, Tag
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
        tags: List[Tag]
        url: Optional[str]

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
                {t.name: t
                 for t in uow.smart_list_tag_repository.find_all_for_smart_list(
                     smart_list_ref_id=smart_list.ref_id, filter_names=args.tags)}
            for tag in args.tags:
                if tag in smart_list_tags:
                    continue
                smart_list_tag = SmartListTag.new_smart_list_tag(
                    smart_list_ref_id=smart_list.ref_id, name=tag, created_time=self._time_provider.get_current_time())
                smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
                smart_list_tags[smart_list_tag.name] = smart_list_tag
            smart_list_item = SmartListItem.new_smart_list_item(
                archived=False, smart_list_ref_id=smart_list.ref_id, name=args.name, is_done=args.is_done,
                tags_ref_id=[t.ref_id for t in smart_list_tags.values()], url=args.url,
                created_time=self._time_provider.get_current_time())
            smart_list_item = uow.smart_list_item_repository.create(smart_list_item)
        for smart_list_tag in smart_list_tags.values():
            self._notion_manager.upsert_smart_list_tag(smart_list_tag)
        self._notion_manager.upsert_smart_list_item(smart_list_item, smart_list_tags.keys())
