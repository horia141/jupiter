"""The use case for loading the home."""

from jupiter.core.domain.application.home.home_big_screen_tab import HomeBigScreenTab
from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@use_case_args
class HomeConfigLoadArgs(UseCaseArgsBase):
    """The arguments for the home config load use case."""


@use_case_result
class HomeConfigLoadResult(UseCaseResultBase):
    """The result of the home config load use case."""

    home_config: HomeConfig
    big_screen_tabs: list[HomeBigScreenTab]
    small_screen_tabs: list[HomeSmallScreenTab]


class HomeConfigLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HomeConfigLoadArgs, HomeConfigLoadResult]
):
    """The use case for loading the home config."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: HomeConfigLoadArgs,
    ) -> HomeConfigLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        big_screen_tabs = await uow.get_for(HomeBigScreenTab).find_all(
            parent_ref_id=home_config.ref_id,
            allow_archived=False,
            filter_ref_ids=home_config.order_of_big_screen_tabs,
        )
        small_screen_tabs = await uow.get_for(HomeSmallScreenTab).find_all(
            parent_ref_id=home_config.ref_id,
            allow_archived=False,
            filter_ref_ids=home_config.order_of_small_screen_tabs,
        )

        return HomeConfigLoadResult(
            home_config=home_config,
            big_screen_tabs=big_screen_tabs,
            small_screen_tabs=small_screen_tabs,
        )
