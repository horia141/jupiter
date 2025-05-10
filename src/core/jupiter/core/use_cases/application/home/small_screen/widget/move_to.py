"""The use case for moving a home small screen widget."""

from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.application.home.home_small_screen_widget import HomeSmallScreenWidget
from jupiter.core.domain.application.home.widget import WidgetDimension
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeSmallScreenWidgetMoveAndResizeArgs(UseCaseArgsBase):
    """The arguments for moving a home small screen widget."""

    ref_id: EntityId
    row: int


class HomeSmallScreenWidgetMoveAndResizeUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeSmallScreenWidgetMoveAndResizeArgs, None]
):
    """The use case for moving a home small screen widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeSmallScreenWidgetMoveAndResizeArgs,
    ) -> None:
        """Execute the command's action."""
        widget = await uow.get_for(HomeSmallScreenWidget).load_by_id(args.ref_id)

        tab = await uow.get_for(HomeSmallScreenTab).load_by_id(
            widget.home_small_screen_tab.ref_id
        )
        
        tab = tab.move_widget_to(
            context.domain_context,
            widget_ref_id=args.ref_id,
            row=args.row,
            dimension=widget.dimension
        )
        
        await uow.get_for(HomeSmallScreenTab).save(tab)
        await progress_reporter.mark_updated(tab)
