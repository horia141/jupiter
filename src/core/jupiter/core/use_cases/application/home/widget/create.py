"""The use case for creating a home small screen widget."""

from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.application.home.widget import (
    WidgetDimension,
    WidgetGeometry,
    WidgetType,
)
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
    mutation_use_case,
)


@use_case_args
class HomeWidgetCreateArgs(UseCaseArgsBase):
    """The arguments for the create home widget use case."""

    home_tab_ref_id: EntityId
    the_type: WidgetType
    row: int
    col: int
    dimension: WidgetDimension

@use_case_result
class HomeWidgetCreateResult(UseCaseResultBase):
    """The result of the create home widget use case."""

    new_widget: HomeWidget


@mutation_use_case()
class HomeWidgetCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeWidgetCreateArgs, HomeWidgetCreateResult]
):
    """The use case for creating a home small screen widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeWidgetCreateArgs,
    ) -> HomeWidgetCreateResult:
        """Execute the command's action."""
        home_tab = await uow.get_for(HomeTab).load_by_id(
            args.home_tab_ref_id,
        )

        home_widget = HomeWidget.new_home_widget(
            context.domain_context,
            home_tab_ref_id=home_tab.ref_id,
            home_tab_target=home_tab.target,
            the_type=args.the_type,
            geometry=WidgetGeometry(
                row=args.row, col=args.col, dimension=args.dimension
            ),
        )
        home_widget = await uow.get_for(HomeWidget).create(home_widget)
        await progress_reporter.mark_created(home_widget)

        home_tab = home_tab.add_widget(
            context.domain_context,
            widget_ref_id=home_widget.ref_id,
            geometry=WidgetGeometry(
                row=args.row, col=args.col, dimension=args.dimension
            ),
        )
        await uow.get_for(HomeTab).save(home_tab)
        await progress_reporter.mark_updated(home_tab)

        return HomeWidgetCreateResult(new_widget=home_widget)
