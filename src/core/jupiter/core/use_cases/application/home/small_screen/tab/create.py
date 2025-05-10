"""The use case for creating a home small screen tab."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeSmallScreenTabCreateArgs(UseCaseArgsBase):
    """The arguments for the create home small screen tab use case."""

    name: EntityName
    icon: EntityIcon | None


class HomeSmallScreenTabCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeSmallScreenTabCreateArgs, None]
):
    """The use case for creating a home small screen tab."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeSmallScreenTabCreateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        home_small_screen_tab = HomeSmallScreenTab.new_home_small_screen_tab(
            context.domain_context,
            home_config_ref_id=home_config.ref_id,
            name=args.name,
            icon=args.icon,
        )
        home_small_screen_tab = await uow.get_for(HomeSmallScreenTab).create(home_small_screen_tab)
        await progress_reporter.mark_created(home_small_screen_tab)

        home_config = home_config.add_small_screen_tab(
            context.domain_context,
            home_small_screen_tab.ref_id,
        )
        await uow.get_for(HomeConfig).save(home_config)
