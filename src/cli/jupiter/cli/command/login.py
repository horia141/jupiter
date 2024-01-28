"""Command for logging in."""

from jupiter.cli.command.command import GuestReadonlyCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.login import LoginResult, LoginUseCase
from rich.console import Console


@secure_class
class Login(GuestReadonlyCommand[LoginUseCase]):
    """Command for logging in."""

    def _render_result(self, console: Console, result: LoginResult) -> None:
        self._session_storage.store(SessionInfo(auth_token_ext=result.auth_token_ext))
