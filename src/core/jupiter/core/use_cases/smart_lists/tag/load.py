"""Use case for loading a smart list tag."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class SmartListTagLoadArgs(UseCaseArgsBase):
    """SmartListTagLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class SmartListTagLoadResult(UseCaseResultBase):
    """SmartListTagLoadResult."""

    smart_list_tag: SmartListTag


@readonly_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListTagLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        SmartListTagLoadArgs, SmartListTagLoadResult
    ]
):
    """Use case for loading a smart list tag."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SmartListTagLoadArgs,
    ) -> SmartListTagLoadResult:
        """Execute the command's action."""
        smart_list_tag = await uow.smart_list_tag_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        return SmartListTagLoadResult(smart_list_tag=smart_list_tag)
