"""The use case for updating the home config."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@use_case_args
class HomeConfigUpdateArgs(UseCaseArgsBase):
    """The arguments for updating the home config."""


class HomeConfigUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[HomeConfigUpdateArgs, None]
):
    """The use case for updating the home config."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HomeConfigUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        home_config = await uow.get_for(HomeConfig).load_by_parent(workspace.ref_id)

        updated_home_config = home_config.update(
            ctx=context.domain_context,
        )
        updated_home_config = await uow.get_for(HomeConfig).save(updated_home_config)
