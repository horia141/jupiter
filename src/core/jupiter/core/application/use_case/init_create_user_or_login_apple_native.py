"""Use case for creating or logging in a user after native Apple sign in."""

from jupiter.core.application.service.apple_login import AppleLoginService
from jupiter.core.application.use_case.init_create_user_or_login_apple import (
    InitCreateUserOrLoginAppleResult,
)
from jupiter.core.auth.sub.apple.apple_auth_code import AppleAuthCode
from jupiter.core.config import (
    JupiterGuestMutationContext,
    JupiterGuestMutationUseCase,
)
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.secure import secure_class
from jupiter.framework.use_case_io import UseCaseArgsBase, use_case_args


@use_case_args
class InitCreateUserOrLoginAppleNativeArgs(UseCaseArgsBase):
    """Init create user or login (native Apple sign in) use case arguments."""

    # The authorizationCode from the Apple SDK in the app shell.
    apple_auth_code: AppleAuthCode
    # Apple sends the name once, and outside the token.
    apple_user_json: str | None


@secure_class
class InitCreateUserOrLoginAppleNativeUseCase(
    JupiterGuestMutationUseCase[
        InitCreateUserOrLoginAppleNativeArgs, InitCreateUserOrLoginAppleResult
    ]
):
    """Use case for creating or logging in a user after native Apple sign in.

    The Apple SDK in the app shell has no redirect, so there is no callback URI.
    """

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterGuestMutationContext,
        args: InitCreateUserOrLoginAppleNativeArgs,
    ) -> InitCreateUserOrLoginAppleResult:
        """Execute the command's action."""
        service = AppleLoginService(
            self._ports,
            self._global_properties,
            self._time_provider,
            self._auth_token_stamper,
        )
        service.check_enabled()
        assert self._ports.apple_oauth_client is not None

        apple_user_info = (
            await self._ports.apple_oauth_client.get_user_info_from_native_code(
                args.apple_auth_code.code_raw,
                args.apple_user_json,
            )
        )

        user, auth_token_ext = await service.create_or_login(context, apple_user_info)
        return InitCreateUserOrLoginAppleResult(
            new_user=user, auth_token_ext=auth_token_ext
        )
