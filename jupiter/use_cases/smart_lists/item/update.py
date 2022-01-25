"""The command for updating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.url import URL
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class SmartListItemUpdateUseCase(AppMutationUseCase['SmartListItemUpdateUseCase.Args', None]):
    """The command for updating a smart list item."""

    @dataclass()
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        name: UpdateAction[SmartListItemName]
        is_done: UpdateAction[bool]
        tags: UpdateAction[List[SmartListTagName]]
        url: UpdateAction[Optional[URL]]

    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_item = uow.smart_list_item_repository.load_by_id(args.ref_id)

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
                        source=EventSource.CLI, created_time=self._time_provider.get_current_time())
                    smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
                    smart_list_tags[smart_list_tag.tag_name] = smart_list_tag
                tags_ref_id = UpdateAction.change_to(
                    [t.ref_id for t in smart_list_tags.values()])
            else:
                tags_ref_id = UpdateAction.do_nothing()

            smart_list_item = smart_list_item.update(
                name=args.name,
                is_done=args.is_done,
                tags_ref_id=tags_ref_id,
                url=args.url,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time())

            uow.smart_list_item_repository.save(smart_list_item)

        for smart_list_tag in smart_list_tags.values():
            notion_smart_list_tag = NotionSmartListTag.new_notion_row(smart_list_tag, None)
            self._smart_list_notion_manager.upsert_smart_list_tag(
                smart_list_item.smart_list_ref_id, notion_smart_list_tag)
        notion_smart_list_item = \
            self._smart_list_notion_manager.load_smart_list_item(
                smart_list_item.smart_list_ref_id, smart_list_item.ref_id)
        notion_smart_list_item = notion_smart_list_item.join_with_aggregate_root(
            smart_list_item,
            NotionSmartListItem.DirectExtraInfo({t.ref_id: t for t in smart_list_tags.values()}))
        self._smart_list_notion_manager.save_smart_list_item(smart_list_item.smart_list_ref_id, notion_smart_list_item)
