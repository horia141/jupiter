"""Specific exception handling."""
import sys

from jupiter.core.domain.journals.journal import JournalExistsForDatePeriodCombinationError
from jupiter.core.domain.time_plans.time_plan import TimePlanExistsForDatePeriodCombinationError

from jupiter.cli.command.command import CliApp, CliExceptionHandler
from jupiter.cli.session_storage import SessionInfoNotFoundError
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.user.user import UserAlreadyExistsError, UserNotFoundError
from jupiter.core.domain.workspaces.workspace import WorkspaceNotFoundError
from jupiter.core.framework.errors import (
    InputValidationError,
    MultiInputValidationError,
)
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.framework.storage import ConnectionPrepareError
from jupiter.core.use_cases.login import InvalidLoginCredentialsError
from rich.console import Console


class SessionInfoNotFoundHandler(CliExceptionHandler[SessionInfoNotFoundError]):
    """Handle the session info not found error."""

    def handle(
        self, app: CliApp, console: Console, exception: SessionInfoNotFoundError
    ) -> None:
        """Handle the session info not found error."""
        console.print("No session info found. Please log in or create a new account.")
        console.print(f"Checkout '{app._global_properties.docs_init_workspace_url}'.")
        sys.exit(1)


class InputValidationHandler(CliExceptionHandler[InputValidationError]):
    """Handle input validation errors."""

    def handle(
        self, app: CliApp, console: Console, exception: InputValidationError
    ) -> None:
        """Handle input validation errors."""
        print("Looks like there's something wrong with the command's arguments:")
        print(f"  {exception}")
        sys.exit(1)


class MultiInputValidationHandler(CliExceptionHandler[MultiInputValidationError]):
    """Handle input validation errors."""

    def handle(
        self, app: CliApp, console: Console, exception: MultiInputValidationError
    ) -> None:
        """Handle input validation errors."""
        print("Looks like there's something wrong with the command's arguments:")
        for k, v in exception.errors.items():
            print(f"  {k}: {v}")
        sys.exit(1)


class FeatureUnavailableHandler(CliExceptionHandler[FeatureUnavailableError]):
    """Handle feature unavailable errors."""

    def handle(
        self, app: CliApp, console: Console, exception: FeatureUnavailableError
    ) -> None:
        """Handle feature unavailable errors."""
        console.print(f"{exception}")
        sys.exit(1)


class UserAlreadyExistsHandler(CliExceptionHandler[UserAlreadyExistsError]):
    """Handle user already exists errors."""

    def handle(
        self, app: CliApp, console: Console, exception: UserAlreadyExistsError
    ) -> None:
        """Handle user already exists errors."""
        print("A user with the same identity already seems to exist here!")
        print("Please try creating another user.")
        sys.exit(1)


class ExpiredAuthTokenandler(CliExceptionHandler[ExpiredAuthTokenError]):
    """Handle expired auth token errors."""

    def handle(
        self, app: CliApp, console: Console, exception: ExpiredAuthTokenError
    ) -> None:
        """Handle expired auth token errors."""
        print("Your authentication token has expired.")
        print("Please log in again.")
        sys.exit(1)


class InvalidLoginCredentialsHandler(CliExceptionHandler[InvalidLoginCredentialsError]):
    """Handle invalid login credentials errors."""

    def handle(
        self, app: CliApp, console: Console, exception: InvalidLoginCredentialsError
    ) -> None:
        """Handle invalid login credentials errors."""
        print("The user and/or password are invalid!")
        print("You can:")
        print(" * Run `login` to login.")
        print(" * Run 'init' to create a user and workspace!")
        print(" * Run 'reset-password' to reset your password!")
        print(
            f"For more information checkout: {app.global_properties.docs_init_workspace_url}",
        )
        sys.exit(1)


class ProjectInSignificantUseHandler(CliExceptionHandler[ProjectInSignificantUseError]):
    """Handle project in significant use errors."""

    def handle(
        self, app: CliApp, console: Console, exception: ProjectInSignificantUseError
    ) -> None:
        """Handle project in significant use errors."""
        print(f"The selected project is still being used. Reason: {exception}")
        print("Please select a backup project via --backup-project-id")
        sys.exit(1)


class TimePlanExistsForDatePeriodCombinationHandler(CliExceptionHandler[TimePlanExistsForDatePeriodCombinationError]):
    """Handle time plans already existing."""

    def handle(
        self, app: CliApp, console: Console, exception: TimePlanExistsForDatePeriodCombinationError
    ) -> None:
        """Handle time plans already existing."""
        print(f"A time plan for that particular day and period already exists")
        sys.exit(1)


class JournalExistsForDatePeriodCombinationHandler(CliExceptionHandler[JournalExistsForDatePeriodCombinationError]):
    """Handle journal already existing."""

    def handle(
        self, app: CliApp, console: Console, exception: JournalExistsForDatePeriodCombinationError
    ) -> None:
        """Handle journal already existing."""
        print(f"A journal for that particular day and period already exists")
        sys.exit(1)


class InvalidAuthTokenHandler(CliExceptionHandler[InvalidAuthTokenError]):
    """Handle invalid auth token errors."""

    def handle(
        self, app: CliApp, console: Console, exception: InvalidAuthTokenError
    ) -> None:
        """Handle invalid auth token errors."""
        print(
            "Your session seems to be invalid! Please run 'init' or 'login' to fix this!"
        )
        print(
            f"For more information checkout: {app.global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)


class ConnectionPrepareHandler(CliExceptionHandler[ConnectionPrepareError]):
    """Handle connection prepare errors."""

    def handle(
        self, app: CliApp, console: Console, exception: ConnectionPrepareError
    ) -> None:
        """Handle connection prepare errors."""
        print("A connection to the database couldn't be established!")
        print("Check if the database path exists")
        print(exception.__traceback__)
        sys.exit(2)


class UserNotFoundHandler(CliExceptionHandler[UserNotFoundError]):
    """Handle user not found errors."""

    def handle(
        self, app: CliApp, console: Console, exception: UserNotFoundError
    ) -> None:
        """Handle user not found errors."""
        print(
            "The user you're trying to operate as does't seem to exist! Please run `init` to create a user and workspace."
        )
        print(
            f"For more information checkout: {app.global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)


class WorkspaceNotFoundHandler(CliExceptionHandler[WorkspaceNotFoundError]):
    """Handle workspace not found errors."""

    def handle(
        self, app: CliApp, console: Console, exception: WorkspaceNotFoundError
    ) -> None:
        """Handle workspace not found errors."""
        print(
            "The workspace you're trying to operate in does't seem to exist! Please run `init` to create a user and workspace."
        )
        print(
            f"For more information checkout: {app.global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)


class EntityNotFoundHandler(CliExceptionHandler[EntityNotFoundError]):
    """Handle entity not found errors."""

    def handle(
        self, app: CliApp, console: Console, exception: EntityNotFoundError
    ) -> None:
        """Handle entity not found errors."""
        print(str(exception))
        sys.exit(1)
