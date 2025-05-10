"""The command for updating a home small screen tab's properties."""

from jupiter.core.domain.application.home.home_small_screen_tab import HomeSmallScreenTab
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class HomeSmallScreenTabUpdateArgs(UseCaseArgsBase):
    """The arguments for updating a home small screen tab."""

    ref_id: EntityId
    name: UpdateAction[EntityName]
    icon: UpdateAction[EntityIcon | None]


@mutation_use_case(None)
class HomeSmallScreenTabUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeSmallScreenTabUpdateArgs, None]
):
    """The command for updating a home small screen tab's properties."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeSmallScreenTabUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        home_small_screen_tab = await uow.get_for(HomeSmallScreenTab).load_by_id(
            args.ref_id,
        )

        home_small_screen_tab = home_small_screen_tab.update(
            context.domain_context,
            name=args.name,
            icon=args.icon,
        )

        await uow.get_for(HomeSmallScreenTab).save(home_small_screen_tab)
        await progress_reporter.mark_updated(home_small_screen_tab) 