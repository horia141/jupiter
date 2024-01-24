"""Command for resetting a password."""
from argparse import ArgumentParser, Namespace
from typing import cast

from jupiter.cli.command.command import GuestMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.auth.reset_password import (
    ResetPasswordArgs,
    ResetPasswordUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from rich.console import Console
from rich.text import Text


@secure_class
class ResetPassword(GuestMutationCommand[ResetPasswordUseCase]):
    """Use case for resetting a password."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--email-address",
            type=str,
            dest="email_address",
            required=True,
            help="The user's email address",
        )
        parser.add_argument(
            "--recovery-token",
            type=RecoveryTokenPlain.from_raw,
            dest="recovery_token",
            required=True,
            help="The recovery token for the user",
        )
        parser.add_argument(
            "--new-password",
            type=PasswordNewPlain.from_raw,
            dest="new_password",
            required=True,
            help="The new password",
        )
        parser.add_argument(
            "--new-password-repeat",
            type=PasswordNewPlain.from_raw,
            dest="new_password_repeat",
            required=True,
            help="A repeat of the new password",
        )

    async def _run(
        self,
        session_info: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        email_address = EmailAddress.from_raw(args.email_address)
        recovery_token = cast(RecoveryTokenPlain, args.recovery_token)
        new_password = cast(PasswordNewPlain, args.new_password)
        new_password_repeat = cast(PasswordNewPlain, args.new_password_repeat)

        result = await self._use_case.execute(
            AppGuestUseCaseSession(
                session_info.auth_token_ext if session_info else None
            ),
            ResetPasswordArgs(
                email_address=email_address,
                recovery_token=recovery_token,
                new_password=new_password,
                new_password_repeat=new_password_repeat,
            ),
        )

        rich_text = Text("Your recovery token is ")
        rich_text.append(result.new_recovery_token.token, style="bold green")
        rich_text.append("\nStore it in a safe place!", style="bold red")

        console = Console()
        console.print(rich_text)

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should print a summary prologue and epilogue."""
        return False
