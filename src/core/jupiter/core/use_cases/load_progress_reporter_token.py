"""The command for loading a progress reporter specific token."""
from dataclasses import dataclass

from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class LoadProgressReporterTokenArgs(UseCaseArgsBase):
    """Load progress reporter token args."""


@dataclass
class LoadProgressReporterTokenResult(UseCaseResultBase):
    """Get progress reporter token result."""

    progress_reporter_token_ext: AuthTokenExt


class LoadProgressReporterTokenUseCase(
    AppLoggedInReadonlyUseCase[
        LoadProgressReporterTokenArgs, LoadProgressReporterTokenResult
    ]
):
    """The use case for retrieving summaries about entities."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: LoadProgressReporterTokenArgs,
    ) -> LoadProgressReporterTokenResult:
        """Execute the command."""
        auth_token = self._auth_token_stamper.stamp_for_progress_reporter(context.user)
        return LoadProgressReporterTokenResult(
            progress_reporter_token_ext=auth_token.to_ext()
        )
