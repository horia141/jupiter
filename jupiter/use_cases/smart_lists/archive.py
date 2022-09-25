"""The command for archiving a smart list."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
    NotionSmartListNotFoundError,
    NotionSmartListTagNotFoundError,
    NotionSmartListItemNotFoundError,
)
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
    MarkProgressStatus,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListArchiveUseCase(AppMutationUseCase["SmartListArchiveUseCase.Args", None]):
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
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )

            smart_list = uow.smart_list_repository.load_by_key(
                smart_list_collection.ref_id, args.key
            )

            smart_list_tags = uow.smart_list_tag_repository.find_all(smart_list.ref_id)
            smart_list_items = uow.smart_list_item_repository.find_all(
                smart_list.ref_id
            )

        for smart_list_tag in smart_list_tags:
            with progress_reporter.start_archiving_entity(
                "smart list tag", smart_list_tag.ref_id, str(smart_list_tag.tag_name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    smart_list_tag = smart_list_tag.mark_archived(
                        EventSource.CLI, self._time_provider.get_current_time()
                    )
                    uow.smart_list_tag_repository.save(smart_list_tag)
                    entity_reporter.mark_local_change()

                try:
                    self._smart_list_notion_manager.remove_branch_tag(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_tag.ref_id,
                    )
                    entity_reporter.mark_remote_change()
                except NotionSmartListTagNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because smart list tag was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        for smart_list_item in smart_list_items:
            with progress_reporter.start_archiving_entity(
                "smart list item", smart_list_item.ref_id, str(smart_list_item.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    smart_list_item = smart_list_item.mark_archived(
                        EventSource.CLI, self._time_provider.get_current_time()
                    )
                    uow.smart_list_item_repository.save(smart_list_item)
                    entity_reporter.mark_local_change()

                try:
                    self._smart_list_notion_manager.remove_leaf(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_item.ref_id,
                    )
                    entity_reporter.mark_remote_change()
                except NotionSmartListItemNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because smart list item was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        with progress_reporter.start_archiving_entity(
            "smart list", smart_list.ref_id, str(smart_list.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                smart_list = smart_list.mark_archived(
                    EventSource.CLI, self._time_provider.get_current_time()
                )
                uow.smart_list_repository.save(smart_list)
                entity_reporter.mark_local_change()

            try:
                self._smart_list_notion_manager.remove_branch(
                    smart_list_collection.ref_id, smart_list.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionSmartListNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because smart list was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
