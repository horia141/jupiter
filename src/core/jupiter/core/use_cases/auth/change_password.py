"""Use case for changing a password."""
from dataclasses import dataclass

from jupiter.core.domain.auth.auth import IncorrectPasswordError
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


class InvalidChangePasswordCredentialsError(Exception):
    """Error raised when the old password isn't good."""


@dataclass
class ChangePasswordArgs(UseCaseArgsBase):
    """Change password args."""

    current_password: PasswordPlain
    new_password: PasswordNewPlain
    new_password_repeat: PasswordNewPlain


@secure_class
class ChangePasswordUseCase(AppLoggedInMutationUseCase[ChangePasswordArgs, None]):
    """Use case for changing a password."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChangePasswordArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            try:
                auth = await uow.auth_repository.load_by_parent(context.user.ref_id)
                auth = auth.change_password(
                    current_password=args.current_password,
                    new_password=args.new_password,
                    new_password_repeat=args.new_password_repeat,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                auth = await uow.auth_repository.save(auth)
            except IncorrectPasswordError as err:
                raise InvalidChangePasswordCredentialsError("Invalid password") from err
