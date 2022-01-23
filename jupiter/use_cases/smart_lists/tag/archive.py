"""The command for archiving a smart list tag."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListTagNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListTagArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a smart list tag."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_tag = uow.smart_list_tag_repository.load_by_id(args)

            smart_list_items = uow.smart_list_item_repository.find_all(
                allow_archived=True,
                filter_smart_list_ref_ids=[smart_list_tag.smart_list_ref_id],
                filter_tag_ref_ids=[args])

            for smart_list_item in smart_list_items:
                smart_list_item = smart_list_item.update(
                    name=UpdateAction.do_nothing(),
                    is_done=UpdateAction.do_nothing(),
                    tags_ref_id=UpdateAction.change_to([t for t in smart_list_item.tags_ref_id if t != args]),
                    url=UpdateAction.do_nothing(),
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

            smart_list_tag = smart_list_tag.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.smart_list_tag_repository.save(smart_list_tag)

        try:
            self._smart_list_notion_manager.remove_smart_list_tag(
                smart_list_tag.smart_list_ref_id, smart_list_tag.ref_id)
        except NotionSmartListTagNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
