"""Use case for creating or logging in a user after Google OAuth callback."""

from jupiter.core.application.service.google_login import GoogleLoginService
from jupiter.core.auth.sub.google.google_auth_code import GoogleAuthCode
from jupiter.core.common.system_url import SystemUrl
from jupiter.core.config import (
    JupiterGuestMutationContext,
    JupiterGuestMutationUseCase,
)
from jupiter.core.users.root import User
from jupiter.framework.auth.auth_token_ext import AuthTokenExt
from jupiter.framework.progress_reporter.reporter import (
    ProgressReporter,
)
from jupiter.framework.secure import secure_class
from jupiter.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)


@use_case_args
class InitCreateUserOrLoginGoogleArgs(UseCaseArgsBase):
    """Init create user or login (Google auth) use case arguments."""

    google_auth_code: GoogleAuthCode
    callback_uri: SystemUrl


@use_case_result
class InitCreateUserOrLoginGoogleResult(UseCaseResultBase):
    """Init create user or login (Google auth) use case result."""

    new_user: User
    auth_token_ext: AuthTokenExt


@secure_class
class InitCreateUserOrLoginGoogleUseCase(
    JupiterGuestMutationUseCase[
        InitCreateUserOrLoginGoogleArgs, InitCreateUserOrLoginGoogleResult
    ]
):
    """Use case for creating or logging in a user after Google OAuth callback."""

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterGuestMutationContext,
        args: InitCreateUserOrLoginGoogleArgs,
    ) -> InitCreateUserOrLoginGoogleResult:
        """Execute the command's action."""
        service = GoogleLoginService(
            self._ports,
            self._global_properties,
            self._time_provider,
            self._auth_token_stamper,
        )
        service.check_enabled()
        assert self._ports.google_oauth_client is not None

        google_user_info = await self._ports.google_oauth_client.get_user_info(
            args.google_auth_code.code_raw,
            args.callback_uri,
        )

        user, auth_token_ext = await service.create_or_login(context, google_user_info)
        return InitCreateUserOrLoginGoogleResult(
            new_user=user, auth_token_ext=auth_token_ext
        )
