"""The command for removing a smart list item."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListItemRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListItemRemoveUseCase(
    AppLoggedInMutationUseCase[SmartListItemRemoveArgs, None]
):
    """The command for removing a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_removing_entity(
            "smart list item",
            args.ref_id,
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                smart_list_item = await uow.smart_list_item_repository.remove(
                    args.ref_id,
                )
                await entity_reporter.mark_known_name(str(smart_list_item.name))
                await entity_reporter.mark_local_change()
