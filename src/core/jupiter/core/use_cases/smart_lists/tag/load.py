"""Use case for loading a smart list tag."""
from dataclasses import dataclass

from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListTagLoadArgs(UseCaseArgsBase):
    """SmartListTagLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class SmartListTagLoadResult(UseCaseResultBase):
    """SmartListTagLoadResult."""

    smart_list_tag: SmartListTag


class SmartListTagLoadUseCase(
    AppLoggedInReadonlyUseCase[SmartListTagLoadArgs, SmartListTagLoadResult]
):
    """Use case for loading a smart list tag."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagLoadArgs,
    ) -> SmartListTagLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            smart_list_tag = await uow.smart_list_tag_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )

        return SmartListTagLoadResult(smart_list_tag=smart_list_tag)
