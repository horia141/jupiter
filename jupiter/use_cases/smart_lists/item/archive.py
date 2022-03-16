"""The command for archiving a smart list item."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListItemNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListItemArchiveUseCase(AppMutationUseCase['SmartListItemArchiveUseCase.Args', None]):
    """The command for archiving a smart list item."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

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
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(workspace.ref_id)

            smart_list_item = uow.smart_list_item_repository.load_by_id(args.ref_id)
            smart_list_item = smart_list_item.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.smart_list_item_repository.save(smart_list_item)

        try:
            self._smart_list_notion_manager.remove_leaf(
                smart_list_collection.ref_id, smart_list_item.smart_list_ref_id, smart_list_item.ref_id)
        except NotionSmartListItemNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
