"""Use case for logging in as a particular user."""
from dataclasses import dataclass

from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.user.infra.user_repository import UserNotFoundError
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestReadonlyUseCase,
    AppGuestUseCaseContext,
)


class InvalidLoginCredentialsError(Exception):
    """Error raised when either an email address or password are not good."""


@dataclass
class LoginArgs(UseCaseArgsBase):
    """Login arguments."""

    email_address: EmailAddress
    password: PasswordPlain


@dataclass
class LoginResult(UseCaseResultBase):
    """Login result."""

    auth_token_ext: AuthTokenExt


@secure_class
class LoginUseCase(AppGuestReadonlyUseCase[LoginArgs, LoginResult]):
    """Use case for logging in as a particular user."""

    async def _execute(
        self,
        context: AppGuestUseCaseContext,
        args: LoginArgs,
    ) -> LoginResult:
        """Execute the command."""
        async with self._storage_engine.get_unit_of_work() as uow:
            try:
                user = await uow.user_repository.load_by_email_address(
                    args.email_address
                )
                auth = await uow.auth_repository.load_by_parent(user.ref_id)

                if not auth.check_password_against(args.password):
                    raise InvalidLoginCredentialsError("User email or password invalid")
            except UserNotFoundError as err:
                raise InvalidLoginCredentialsError(
                    "User email or password invalid"
                ) from err

            auth_token = self._auth_token_stamper.stamp_for_general(user)

            return LoginResult(auth_token_ext=auth_token.to_ext())
