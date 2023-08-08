"""The command for hard removing a smart list."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListRemoveUseCase(AppLoggedInMutationUseCase[SmartListRemoveArgs, None]):
    """The command for removing a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            smart_list_collection = (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            smart_list = await uow.smart_list_repository.load_by_id(
                args.ref_id, allow_archived=True
            )

        smart_list_remove_service = SmartListRemoveService(
            self._domain_storage_engine,
        )
        await smart_list_remove_service.execute(
            progress_reporter,
            smart_list_collection,
            smart_list,
        )
