"""The command for archiving a smart list."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SmartListArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListArchiveArgs, None]
):
    """The command for archiving a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.smart_list_repository.load_by_id(args.ref_id)

        smart_list_tags = await uow.smart_list_tag_repository.find_all(
            smart_list.ref_id,
        )
        smart_list_items = await uow.smart_list_item_repository.find_all(
            smart_list.ref_id,
        )

        for smart_list_tag in smart_list_tags:
            smart_list_tag = smart_list_tag.mark_archived(
                EventSource.CLI,
                self._time_provider.get_current_time(),
            )
            await uow.smart_list_tag_repository.save(smart_list_tag)
            await progress_reporter.mark_updated(smart_list_tag)

        for smart_list_item in smart_list_items:
            smart_list_item = smart_list_item.mark_archived(
                EventSource.CLI,
                self._time_provider.get_current_time(),
            )
            await uow.smart_list_item_repository.save(smart_list_item)
            await progress_reporter.mark_updated(smart_list_item)

        smart_list = smart_list.mark_archived(
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.smart_list_repository.save(smart_list)
        await progress_reporter.mark_updated(smart_list)
