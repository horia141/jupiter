"""Use case for creating or logging in a user after Apple OAuth callback."""

from jupiter.core.application.service.apple_login import AppleLoginService
from jupiter.core.auth.sub.apple.apple_auth_code import AppleAuthCode
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
class InitCreateUserOrLoginAppleArgs(UseCaseArgsBase):
    """Init create user or login (Apple auth) use case arguments."""

    apple_auth_code: AppleAuthCode
    callback_uri: SystemUrl
    apple_user_json: str | None


@use_case_result
class InitCreateUserOrLoginAppleResult(UseCaseResultBase):
    """Init create user or login (Apple auth) use case result."""

    new_user: User
    auth_token_ext: AuthTokenExt


@secure_class
class InitCreateUserOrLoginAppleUseCase(
    JupiterGuestMutationUseCase[
        InitCreateUserOrLoginAppleArgs, InitCreateUserOrLoginAppleResult
    ]
):
    """Use case for creating or logging in a user after Apple OAuth callback."""

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterGuestMutationContext,
        args: InitCreateUserOrLoginAppleArgs,
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

        apple_user_info = await self._ports.apple_oauth_client.get_user_info(
            args.apple_auth_code.code_raw,
            args.callback_uri,
            args.apple_user_json,
        )

        user, auth_token_ext = await service.create_or_login(context, apple_user_info)
        return InitCreateUserOrLoginAppleResult(
            new_user=user, auth_token_ext=auth_token_ext
        )
