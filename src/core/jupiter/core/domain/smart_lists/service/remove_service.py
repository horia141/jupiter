"""Shared service for removing a metric."""
from typing import Final

from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.use_case import ProgressReporter


class SmartListRemoveService:
    """Shared service for removing a smart list."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def execute(
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            all_smart_list_tags = await uow.smart_list_tag_repository.find_all(
                smart_list.ref_id,
                allow_archived=True,
            )
            all_smart_list_items = await uow.smart_list_item_repository.find_all(
                smart_list.ref_id,
                allow_archived=True,
            )

            for smart_list_tag in all_smart_list_tags:
                await uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)
                await progress_reporter.mark_removed(smart_list_tag)

            for smart_list_item in all_smart_list_items:
                await uow.smart_list_item_repository.remove(smart_list_item.ref_id)
                await progress_reporter.mark_removed(smart_list_item)

            await uow.smart_list_repository.remove(smart_list.ref_id)
            await progress_reporter.mark_removed(smart_list)
