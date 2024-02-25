"""The command for hard removing a smart list."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class SmartListRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListRemoveArgs, None]
):
    """The command for removing a smart list."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.get_for(SmartList).load_by_id(
            args.ref_id, allow_archived=True
        )

        smart_list_remove_service = SmartListRemoveService()
        await smart_list_remove_service.execute(
            context.domain_context,
            uow,
            progress_reporter,
            smart_list,
        )
