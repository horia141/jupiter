"""The command for updating a user's properties."""

from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class UserUpdateArgs(UseCaseArgsBase):
    """User update args."""

    name: UpdateAction[UserName]
    timezone: UpdateAction[Timezone]


@mutation_use_case()
class UserUpdateUseCase(AppTransactionalLoggedInMutationUseCase[UserUpdateArgs, None]):
    """The command for updating a user's properties."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: UserUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user.update(
            context.domain_context,
            name=args.name,
            timezone=args.timezone,
        )
        await uow.user_repository.save(user)
