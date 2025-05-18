"""The use case for moving a home small screen widget."""

from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.application.home.widget import WidgetDimension
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class HomeWidgetMoveAndResizeArgs(UseCaseArgsBase):
    """The arguments for moving a home widget."""

    ref_id: EntityId
    row: int
    col: int
    dimension: WidgetDimension


@mutation_use_case()
class HomeWidgetMoveAndResizeUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeWidgetMoveAndResizeArgs, None]
):
    """The use case for moving a home widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeWidgetMoveAndResizeArgs,
    ) -> None:
        """Execute the command's action."""
        widget = await uow.get_for(HomeWidget).load_by_id(args.ref_id)
        tab = await uow.get_for(HomeTab).load_by_id(widget.home_tab.ref_id)
        widget = widget.move_and_resize(
            context.domain_context,
            tab.target,
            args.row,
            args.col,
            args.dimension,
        )
        await uow.get_for(HomeWidget).save(widget)
        await progress_reporter.mark_updated(widget)

        tab = tab.move_widget_to(
            context.domain_context,
            widget_ref_id=args.ref_id,
            geometry=widget.geometry,
        )
        await uow.get_for(HomeTab).save(tab)
        await progress_reporter.mark_updated(tab)
