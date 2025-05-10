"""The use case for removing a home small screen widget."""

from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.application.home.home_small_screen_widget import HomeSmallScreenWidget
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeSmallScreenWidgetRemoveArgs(UseCaseArgsBase):
    """The arguments for removing a home small screen widget."""

    ref_id: EntityId


class HomeSmallScreenWidgetRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeSmallScreenWidgetRemoveArgs, None]
):
    """The use case for removing a home small screen widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeSmallScreenWidgetRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        widget = await uow.get_for(HomeSmallScreenWidget).load_by_id(args.ref_id)
        
        # First remove widget from tab
        tab = await uow.get_for(HomeSmallScreenTab).load_by_id(
            widget.home_small_screen_tab.ref_id
        )
        tab = tab.remove_widget(context.domain_context, widget.ref_id)
        await uow.get_for(HomeSmallScreenTab).save(tab)
        await progress_reporter.mark_updated(tab)

        await generic_crown_remover(
            context.domain_context, uow, progress_reporter, HomeSmallScreenWidget, args.ref_id
        )
