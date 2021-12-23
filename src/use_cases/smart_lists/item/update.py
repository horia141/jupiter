"""The command for updating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from domain.url import URL
from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from domain.entity_name import EntityName
from framework.update_action import UpdateAction
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider


class SmartListItemUpdateUseCase(UseCase['SmartListItemUpdateUseCase.Args', None]):
    """The command for updating a smart list item."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[EntityName]
        is_done: UpdateAction[bool]
        tags: UpdateAction[List[SmartListTagName]]
        url: UpdateAction[Optional[URL]]

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
            smart_list_item = uow.smart_list_item_repository.load_by_id(args.ref_id)

            if args.name.should_change:
                smart_list_item.change_name(args.name.value, self._time_provider.get_current_time())
            if args.is_done.should_change:
                smart_list_item.change_is_done(args.is_done.value, self._time_provider.get_current_time())

            if args.tags.should_change:
                smart_list_tags = \
                    {t.tag_name: t
                     for t in uow.smart_list_tag_repository.find_all_for_smart_list(
                         smart_list_ref_id=smart_list_item.smart_list_ref_id, filter_tag_names=args.tags.value)}
                for tag in args.tags.value:
                    if tag in smart_list_tags:
                        continue
                    smart_list_tag = SmartListTag.new_smart_list_tag(
                        smart_list_ref_id=smart_list_item.smart_list_ref_id, tag_name=tag,
                        created_time=self._time_provider.get_current_time())
                    smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
                    smart_list_tags[smart_list_tag.tag_name] = smart_list_tag
                smart_list_item.change_tags(
                    [t.ref_id for t in smart_list_tags.values()], self._time_provider.get_current_time())

            if args.url.should_change:
                smart_list_item.change_url(args.url.value, self._time_provider.get_current_time())

            uow.smart_list_item_repository.save(smart_list_item)

        for smart_list_tag in smart_list_tags.values():
            self._notion_manager.upsert_smart_list_tag(smart_list_tag)
        self._notion_manager.upsert_smart_list_item(smart_list_item, smart_list_tags.keys())
