"""Exceptions handling for the webapi module."""
from fastapi.responses import JSONResponse
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.journals.journal import (
    JournalExistsForDatePeriodCombinationError,
)
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.user.user import UserAlreadyExistsError, UserNotFoundError
from jupiter.core.domain.workspaces.workspace import WorkspaceNotFoundError
from jupiter.core.framework.errors import (
    InputValidationError,
    MultiInputValidationError,
)
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.use_cases.login import InvalidLoginCredentialsError
from jupiter.webapi.app import WebExceptionHandler, WebServiceApp
from starlette import status


class InputValidationHandler(WebExceptionHandler[InputValidationError]):
    """Handle input validation errors."""

    def handle(
        self, app: WebServiceApp, exception: InputValidationError
    ) -> JSONResponse:
        """Handle input validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"{exception}",
                        "type": "value_error.inputvalidationerror",
                    },
                ],
            },
        )


class MultiInputValidationHandler(WebExceptionHandler[MultiInputValidationError]):
    """Handle input validation errors."""

    def handle(
        self, app: WebServiceApp, exception: MultiInputValidationError
    ) -> JSONResponse:
        """Handle input validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                            k,
                        ],
                        "msg": f"{v}",
                        "type": "value_error.inputvalidationerror",
                    }
                    for k, v in exception.errors.items()
                ]
            },
        )


class FeatureUnavailableHandler(WebExceptionHandler[FeatureUnavailableError]):
    """Handle feature unavailable errors."""

    def handle(
        self, app: WebServiceApp, exception: FeatureUnavailableError
    ) -> JSONResponse:
        """Handle feature unavailable errors."""
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=f"{exception}",
        )


class UserAlreadyExistsHandler(WebExceptionHandler[UserAlreadyExistsError]):
    """Handle user already exists errors."""

    def handle(
        self, app: WebServiceApp, exception: UserAlreadyExistsError
    ) -> JSONResponse:
        """Handle user already exists errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"{exception}",
                        "type": "value_error.useralreadyexistserror",
                    },
                ],
            },
        )


class ExpiredAuthTokenandler(WebExceptionHandler[ExpiredAuthTokenError]):
    """Handle expired auth token errors."""

    def handle(
        self, app: WebServiceApp, exception: ExpiredAuthTokenError
    ) -> JSONResponse:
        """Handle expired auth token errors."""
        return JSONResponse(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            content="Your session token seems to be busted",
        )


class InvalidLoginCredentialsHandler(WebExceptionHandler[InvalidLoginCredentialsError]):
    """Handle invalid login credentials errors."""

    def handle(
        self, app: WebServiceApp, exception: InvalidLoginCredentialsError
    ) -> JSONResponse:
        """Handle invalid login credentials errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": "User email or password invalid",
                        "type": "value_error.invalidlogincredentialserror",
                    },
                ],
            },
        )


class ProjectInSignificantUseHandler(WebExceptionHandler[ProjectInSignificantUseError]):
    """Handle project in significant use errors."""

    def handle(
        self, app: WebServiceApp, exception: ProjectInSignificantUseError
    ) -> JSONResponse:
        """Handle project in significant use errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"Cannot remove because: {exception}",
                        "type": "value_error.projectinsignificantuserror",
                    },
                ],
            },
        )


class EntityNotFoundHandler(WebExceptionHandler[EntityNotFoundError]):
    """Handle entity not found errors."""

    def handle(
        self, app: WebServiceApp, exception: EntityNotFoundError
    ) -> JSONResponse:
        """Handle entity not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Entity does not exist",
        )


class InvalidAuthTokenHandler(WebExceptionHandler[InvalidAuthTokenError]):
    """Handle invalid auth token errors."""

    def handle(
        self, app: WebServiceApp, exception: InvalidAuthTokenError
    ) -> JSONResponse:
        """Handle invalid auth token errors."""
        return JSONResponse(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            content="Your session token seems to be busted",
        )


class UserNotFoundHandler(WebExceptionHandler[UserNotFoundError]):
    """Handle user not found errors."""

    def handle(self, app: WebServiceApp, exception: UserNotFoundError) -> JSONResponse:
        """Handle user not found errors."""
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content="User does not exist",
        )


class WorkspaceNotFoundHandler(WebExceptionHandler[WorkspaceNotFoundError]):
    """Handle workspace not found errors."""

    def handle(
        self, app: WebServiceApp, exception: WorkspaceNotFoundError
    ) -> JSONResponse:
        """Handle workspace not found errors."""
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content="Workspace does not exist",
        )


class JournalExistsForDatePeriodCombinationHandler(
    WebExceptionHandler[JournalExistsForDatePeriodCombinationError]
):
    """Handle journal exists for date period combination errors."""

    def handle(
        self, app: WebServiceApp, exception: JournalExistsForDatePeriodCombinationError
    ) -> JSONResponse:
        """Handle journal exists for date period combination errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Journal already exists for this date and period combination",
        )
