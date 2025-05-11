"""The use case for removing a home small screen widget."""

from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
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
class HomeWidgetRemoveArgs(UseCaseArgsBase):
    """The arguments for removing a home widget."""

    ref_id: EntityId


@mutation_use_case()
class HomeWidgetRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeWidgetRemoveArgs, None]
):
    """The use case for removing a home widget."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeWidgetRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        widget = await uow.get_for(HomeWidget).load_by_id(
            args.ref_id, allow_archived=True
        )

        # First remove widget from tab
        tab = await uow.get_for(HomeTab).load_by_id(
            widget.home_tab.ref_id, allow_archived=True
        )
        tab = tab.remove_widget(context.domain_context, widget.ref_id)
        await uow.get_for(HomeTab).save(tab)
        await progress_reporter.mark_updated(tab)

        await generic_crown_remover(
            context.domain_context, uow, progress_reporter, HomeWidget, args.ref_id
        )
