"""The command for archiving a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SmartListTagArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListTagArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListTagArchiveArgs, None]
):
    """The command for archiving a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_tag = await uow.smart_list_tag_repository.load_by_id(args.ref_id)

        smart_list_items = await uow.smart_list_item_repository.find_all_with_filters(
            parent_ref_id=smart_list_tag.smart_list_ref_id,
            allow_archived=True,
            filter_tag_ref_ids=[args.ref_id],
        )

        for smart_list_item in smart_list_items:
            smart_list_item = smart_list_item.update(
                name=UpdateAction.do_nothing(),
                is_done=UpdateAction.do_nothing(),
                tags_ref_id=UpdateAction.change_to(
                    [t for t in smart_list_item.tags_ref_id if t != args.ref_id],
                ),
                url=UpdateAction.do_nothing(),
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )
            await uow.smart_list_item_repository.save(smart_list_item)
            await progress_reporter.mark_updated(smart_list_item)

        smart_list_tag = smart_list_tag.mark_archived(
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.smart_list_tag_repository.save(smart_list_tag)
        await progress_reporter.mark_updated(smart_list_tag)
