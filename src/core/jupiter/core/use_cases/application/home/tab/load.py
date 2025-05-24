"""The use case for loading a home tab and its widgets."""

from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class HomeTabLoadArgs(UseCaseArgsBase):
    """The arguments for loading a home tab."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class HomeTabLoadResult(UseCaseResultBase):
    """The result of loading a home tab."""

    tab: HomeTab
    widgets: list[HomeWidget]


@readonly_use_case()
class HomeTabLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HomeTabLoadArgs, HomeTabLoadResult]
):
    """The use case for loading a home tab."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: HomeTabLoadArgs,
    ) -> HomeTabLoadResult:
        """Execute the use case's action."""
        tab, widgets = await generic_loader(
            uow,
            HomeTab,
            args.ref_id,
            HomeTab.widgets,
            allow_archived=args.allow_archived,
            allow_subentity_archived=True,
        )

        return HomeTabLoadResult(tab=tab, widgets=list(widgets))
