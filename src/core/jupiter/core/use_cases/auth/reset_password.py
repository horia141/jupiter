"""Use case for reseting a password."""
from dataclasses import dataclass

from jupiter.core.domain.auth.auth import IncorrectRecoveryTokenError
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.user.infra.user_repository import UserNotFoundError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestUseCaseContext,
)


class InvalidResetPasswordCredentialsError(Exception):
    """Error raised when either an email address or recovery token are not good."""


@dataclass
class ResetPasswordArgs(UseCaseArgsBase):
    """Reset password args."""

    email_address: EmailAddress
    recovery_token: RecoveryTokenPlain
    new_password: PasswordNewPlain
    new_password_repeat: PasswordNewPlain


@dataclass
class ResetPasswordResult(UseCaseResultBase):
    """Reset password result."""

    new_recovery_token: RecoveryTokenPlain


@secure_class
class ResetPasswordUseCase(
    AppGuestMutationUseCase[ResetPasswordArgs, ResetPasswordResult]
):
    """Use case for reseting a password."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppGuestUseCaseContext,
        args: ResetPasswordArgs,
    ) -> ResetPasswordResult:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity("auth") as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                try:
                    user = await uow.user_repository.load_by_email_address(
                        args.email_address
                    )
                    auth = await uow.auth_repository.load_by_parent(user.ref_id)
                    auth, new_recovery_token = auth.reset_password(
                        recovery_token=args.recovery_token,
                        new_password=args.new_password,
                        new_password_repeat=args.new_password_repeat,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    auth = await uow.auth_repository.save(auth)
                    await entity_reporter.mark_known_entity(auth)
                    await entity_reporter.mark_local_change()
                except (UserNotFoundError, IncorrectRecoveryTokenError) as err:
                    raise InvalidResetPasswordCredentialsError(
                        "Username or recovery token invalid"
                    ) from err

        return ResetPasswordResult(new_recovery_token=new_recovery_token)
