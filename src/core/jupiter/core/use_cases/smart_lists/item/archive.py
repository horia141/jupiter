"""The command for archiving a smart list item."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListItemArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListItemArchiveUseCase(
    AppLoggedInMutationUseCase[SmartListItemArchiveArgs, None]
):
    """The command for archiving a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_archiving_entity(
            "smart list item",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                smart_list_item = await uow.smart_list_item_repository.load_by_id(
                    args.ref_id,
                )
                await entity_reporter.mark_known_name(str(smart_list_item.name))

                smart_list_item = smart_list_item.mark_archived(
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.smart_list_item_repository.save(smart_list_item)
                await entity_reporter.mark_local_change()
