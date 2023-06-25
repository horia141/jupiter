"""Command for changing a password."""
from argparse import ArgumentParser, Namespace
from typing import cast

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.auth.change_password import (
    ChangePasswordArgs,
    ChangePasswordUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


@secure_class
class AuthChangePassword(LoggedInMutationCommand[ChangePasswordUseCase]):
    """Use case for changin a password."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "auth-change-password"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the password for the user"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--current-password",
            type=PasswordPlain.from_raw,
            dest="current_password",
            required=True,
            help="The current password for the user",
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
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        current_password = cast(PasswordPlain, args.current_password)
        new_password = cast(PasswordNewPlain, args.new_password)
        new_password_repeat = cast(PasswordNewPlain, args.new_password_repeat)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ChangePasswordArgs(
                current_password=current_password,
                new_password=new_password,
                new_password_repeat=new_password_repeat,
            ),
        )
