"""Command for resetting a password."""

from jupiter.cli.command.command import GuestMutationCommand
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.auth.reset_password import (
    ResetPasswordResult,
    ResetPasswordUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppGuestMutationUseCaseContext
from rich.console import Console
from rich.text import Text


@secure_class
class ResetPassword(GuestMutationCommand[ResetPasswordUseCase, ResetPasswordResult]):
    """Use case for resetting a password."""

    def _render_result(
        self,
        console: Console,
        context: AppGuestMutationUseCaseContext,
        result: ResetPasswordResult,
    ) -> None:
        rich_text = Text("Your recovery token is ")
        rich_text.append(result.new_recovery_token.token, style="bold green")
        rich_text.append("\nStore it in a safe place!", style="bold red")

        console.print(rich_text)

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should print a summary prologue and epilogue."""
        return False
