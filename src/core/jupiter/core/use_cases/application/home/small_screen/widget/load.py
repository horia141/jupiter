"""The use case for loading a home small screen widget."""

from jupiter.core.domain.application.home.home_small_screen_widget import HomeSmallScreenWidget
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
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@use_case_args
class HomeSmallScreenWidgetLoadArgs(UseCaseArgsBase):
    """The arguments for loading a home small screen widget."""

    ref_id: EntityId


@use_case_result
class HomeSmallScreenWidgetLoadResult(UseCaseResultBase):
    """The result of loading a home small screen widget."""

    widget: HomeSmallScreenWidget


class HomeSmallScreenWidgetLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HomeSmallScreenWidgetLoadArgs, HomeSmallScreenWidgetLoadResult]
):
    """The use case for loading a home small screen widget."""

    async def _perform_transactional(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HomeSmallScreenWidgetLoadArgs,
    ) -> HomeSmallScreenWidgetLoadResult:
        """Execute the use case's action."""
        widget = await uow.get_for(HomeSmallScreenWidget).load_by_id(args.ref_id)
        return HomeSmallScreenWidgetLoadResult(widget=widget)
