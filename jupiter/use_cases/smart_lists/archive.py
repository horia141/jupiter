"""The command for archiving a smart list."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListNotFoundError
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListArchiveUseCase(AppMutationUseCase['SmartListArchiveUseCase.Args', None]):
    """The command for archiving a smart list."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: SmartListKey

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
            smart_list = uow.smart_list_repository.load_by_key(args.key)

            for smart_list_tag in uow.smart_list_tag_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_tag = smart_list_tag.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.smart_list_tag_repository.save(smart_list_tag)

            for smart_list_item in uow.smart_list_item_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_item = smart_list_item.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

            smart_list = smart_list.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.smart_list_repository.save(smart_list)
            LOGGER.info("Applied local changes")

        try:
            self._smart_list_notion_manager.remove_smart_list(smart_list.ref_id)
            LOGGER.info("Applied Notion changes")
        except NotionSmartListNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
