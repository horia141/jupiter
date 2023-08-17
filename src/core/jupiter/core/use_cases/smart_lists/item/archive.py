"""The command for archiving a smart list item."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
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
class SmartListItemArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListItemArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListItemArchiveArgs, None]
):
    """The command for archiving a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_item = await uow.smart_list_item_repository.load_by_id(
            args.ref_id,
        )

        smart_list_item = smart_list_item.mark_archived(
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.smart_list_item_repository.save(smart_list_item)
        await progress_reporter.mark_updated(smart_list_item)
