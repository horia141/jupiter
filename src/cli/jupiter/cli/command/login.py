"""Command for logging in."""
from argparse import ArgumentParser, Namespace
from typing import cast

from jupiter.cli.command.command import GuestReadonlyCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from jupiter.core.use_cases.login import LoginArgs, LoginUseCase


@secure_class
class Login(GuestReadonlyCommand[LoginUseCase]):
    """Command for logging in."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--email",
            dest="email_address",
            required=True,
            help="The email address you use to log in to Jupiter",
        )
        parser.add_argument(
            "--password",
            dest="password",
            type=PasswordPlain.from_raw,
            required=True,
            help="The password you use to log in",
        )

    async def _run(
        self,
        session_info: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        email_address = EmailAddress.from_raw(args.email_address)
        password = cast(PasswordPlain, args.password)

        result = await self._use_case.execute(
            AppGuestUseCaseSession(
                session_info.auth_token_ext if session_info else None
            ),
            LoginArgs(
                email_address=email_address,
                password=password,
            ),
        )

        self._session_storage.store(SessionInfo(auth_token_ext=result.auth_token_ext))
