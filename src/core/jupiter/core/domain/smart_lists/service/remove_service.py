"""Shared service for removing a metric."""

from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class SmartListRemoveService:
    """Shared service for removing a smart list."""

    async def execute(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        smart_list: SmartList,
    ) -> None:
        """Execute the command's action."""
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
