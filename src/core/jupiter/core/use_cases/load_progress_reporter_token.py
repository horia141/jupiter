"""The command for loading a progress reporter specific token."""

from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class LoadProgressReporterTokenArgs(UseCaseArgsBase):
    """Load progress reporter token args."""


@use_case_result
class LoadProgressReporterTokenResult(UseCaseResultBase):
    """Get progress reporter token result."""

    progress_reporter_token_ext: AuthTokenExt


@secure_class
@readonly_use_case()
class LoadProgressReporterTokenUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        LoadProgressReporterTokenArgs, LoadProgressReporterTokenResult
    ]
):
    """The use case for retrieving summaries about entities."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: LoadProgressReporterTokenArgs,
    ) -> LoadProgressReporterTokenResult:
        """Execute the command."""
        auth_token = self._auth_token_stamper.stamp_for_progress_reporter(context.user)
        return LoadProgressReporterTokenResult(
            progress_reporter_token_ext=auth_token.to_ext()
        )
