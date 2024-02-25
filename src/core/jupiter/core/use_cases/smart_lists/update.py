"""The command for updating a smart list."""
from typing import Optional

from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
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
class SmartListUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[SmartListName]
    icon: UpdateAction[Optional[EntityIcon]]


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListUpdateArgs, None]
):
    """The command for updating a smart list."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.get_for(SmartList).load_by_id(
            args.ref_id,
        )

        smart_list = smart_list.update(
            ctx=context.domain_context,
            name=args.name,
            icon=args.icon,
        )

        await uow.get_for(SmartList).save(smart_list)
        await progress_reporter.mark_updated(smart_list)
