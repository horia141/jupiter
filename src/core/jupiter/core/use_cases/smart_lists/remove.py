"""The command for hard removing a smart list."""
from dataclasses import dataclass

from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
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
class SmartListRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListRemoveUseCase(AppLoggedInMutationUseCase[SmartListRemoveArgs, None]):
    """The command for removing a smart list."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            smart_list = await uow.smart_list_repository.load_by_id(
                args.ref_id, allow_archived=True
            )

        smart_list_remove_service = SmartListRemoveService(
            self._storage_engine,
        )
        await smart_list_remove_service.execute(
            progress_reporter,
            smart_list_collection,
            smart_list,
        )
