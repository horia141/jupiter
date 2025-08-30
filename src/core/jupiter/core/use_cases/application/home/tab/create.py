"""The use case for creating a home small screen tab."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
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
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class HomeTabCreateArgs(UseCaseArgsBase):
    """The arguments for the create home tab use case."""

    target: HomeTabTarget
    name: EntityName
    icon: EntityIcon | None


@use_case_result
class HomeTabCreateResult(UseCaseResultBase):
    """The result of the create home tab use case."""

    new_home_tab: HomeTab


@mutation_use_case()
class HomeTabCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeTabCreateArgs, HomeTabCreateResult]
):
    """The use case for creating a home tab."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeTabCreateArgs,
    ) -> HomeTabCreateResult:
        """Execute the command's action."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        home_tab = HomeTab.new_home_tab(
            context.domain_context,
            home_config_ref_id=home_config.ref_id,
            target=args.target,
            name=args.name,
            icon=args.icon,
        )
        home_tab = await uow.get_for(HomeTab).create(home_tab)
        await progress_reporter.mark_created(home_tab)

        home_config = home_config.add_tab(
            context.domain_context,
            target=args.target,
            tab_ref_id=home_tab.ref_id,
        )
        await uow.get_for(HomeConfig).save(home_config)

        return HomeTabCreateResult(new_home_tab=home_tab)
