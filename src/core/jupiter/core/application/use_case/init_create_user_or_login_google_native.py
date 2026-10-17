"""Use case for creating or logging in a user after native Google sign in."""

from jupiter.core.application.service.google_login import GoogleLoginService
from jupiter.core.application.use_case.init_create_user_or_login_google import (
    InitCreateUserOrLoginGoogleResult,
)
from jupiter.core.auth.sub.google.google_auth_code import GoogleAuthCode
from jupiter.core.config import (
    JupiterGuestMutationContext,
    JupiterGuestMutationUseCase,
)
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.secure import secure_class
from jupiter.framework.use_case_io import UseCaseArgsBase, use_case_args


@use_case_args
class InitCreateUserOrLoginGoogleNativeArgs(UseCaseArgsBase):
    """Init create user or login (native Google sign in) use case arguments."""

    # The serverAuthCode from the Google SDK in the app shell.
    google_auth_code: GoogleAuthCode


@secure_class
class InitCreateUserOrLoginGoogleNativeUseCase(
    JupiterGuestMutationUseCase[
        InitCreateUserOrLoginGoogleNativeArgs, InitCreateUserOrLoginGoogleResult
    ]
):
    """Use case for creating or logging in a user after native Google sign in.

    The Google SDK in the app shell has no redirect, so there is no callback URI.
    """

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterGuestMutationContext,
        args: InitCreateUserOrLoginGoogleNativeArgs,
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

        google_user_info = (
            await self._ports.google_oauth_client.get_user_info_from_native_code(
                args.google_auth_code.code_raw,
            )
        )

        user, auth_token_ext = await service.create_or_login(context, google_user_info)
        return InitCreateUserOrLoginGoogleResult(
            new_user=user, auth_token_ext=auth_token_ext
        )
