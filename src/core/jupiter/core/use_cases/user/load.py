"""The command for loading the current user."""
from dataclasses import dataclass

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.user.user import User
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class UserLoadArgs(UseCaseArgsBase):
    """User find args."""


@dataclass
class UserLoadResult(UseCaseResultBase):
    """User find result."""

    user: User


class UserLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[UserLoadArgs, UserLoadResult]
):
    """The command for loading the current user."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: UserLoadArgs,
    ) -> UserLoadResult:
        """Execute the command's action."""
        return UserLoadResult(user=context.user)
