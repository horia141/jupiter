"""The use case for creating a home small screen widget."""

from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.application.home.home_small_screen_widget import HomeSmallScreenWidget
from jupiter.core.domain.application.home.widget import WidgetDimension, WidgetType
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeSmallScreenWidgetCreateArgs(UseCaseArgsBase):
    """The arguments for the create home small screen widget use case."""

    home_small_screen_tab_ref_id: EntityId
    the_type: WidgetType
    row: int
    dimension: WidgetDimension


class HomeSmallScreenWidgetCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeSmallScreenWidgetCreateArgs, None]
):
    """The use case for creating a home small screen widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeSmallScreenWidgetCreateArgs,
    ) -> None:
        """Execute the command's action."""
        home_small_screen_tab = await uow.get_for(HomeSmallScreenTab).load_by_id(
            args.home_small_screen_tab_ref_id,
        )

        home_small_screen_widget = HomeSmallScreenWidget.new_home_small_screen_widget(
            context.domain_context,
            home_small_screen_tab_ref_id=home_small_screen_tab.ref_id,
            the_type=args.the_type,
            dimension=args.dimension,
        )
        home_small_screen_widget = await uow.get_for(HomeSmallScreenWidget).create(home_small_screen_widget)
        await progress_reporter.mark_created(home_small_screen_widget)

        home_small_screen_tab = home_small_screen_tab.add_widget(
            context.domain_context,
            widget_ref_id=home_small_screen_widget.ref_id,
            row=args.row,
            dimension=args.dimension,
        )
        await uow.get_for(HomeSmallScreenTab).save(home_small_screen_tab)
        await progress_reporter.mark_updated(home_small_screen_tab)
