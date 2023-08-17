"""Use case for loading a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
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
    AppTransactionalLoggedInReadOnlyUseCase[
        SmartListTagLoadArgs, SmartListTagLoadResult
    ]
):
    """Use case for loading a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagLoadArgs,
    ) -> SmartListTagLoadResult:
        """Execute the command's action."""
        smart_list_tag = await uow.smart_list_tag_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        return SmartListTagLoadResult(smart_list_tag=smart_list_tag)
