"""The use case for reordering tabs in the home config."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import ProgressReporter, UseCase, UseCaseContext
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class ReorderTabsArgs(UseCaseArgsBase):
    """The arguments for reordering tabs in the home config."""

    target: HomeTabTarget
    order_of_tabs: list[EntityId]


@mutation_use_case()
class ReorderTabsUseCase(AppTransactionalLoggedInMutationUseCase[ReorderTabsArgs, None]):
    """The use case for reordering tabs in the home config."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ReorderTabsArgs,
    ) -> None:
        """Execute the use case."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        tabs = await uow.get_for(HomeTab).find_all_generic(
            parent_ref_id=home_config.ref_id,
            allow_archived=False,
            target=args.target,
        )

        tab_ref_ids = {tab.ref_id for tab in tabs}
        if set(args.order_of_tabs) != tab_ref_ids:
            raise InputValidationError(
                "The new order of tabs does not match the actual tabs."
            )

        home_config = home_config.reoder_tabs(
            ctx=context.domain_context,
            target=args.target,
            order_of_tabs=args.order_of_tabs,
        )
        await uow.get_for(HomeConfig).save(home_config)
