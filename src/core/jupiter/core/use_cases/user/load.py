"""The command for loading the current user."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.gamification.service.score_overview_service import (
    ScoreOverviewService,
)
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.storage_engine import DomainStorageEngine, DomainUnitOfWork
from jupiter.core.domain.user.user import User
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class UserLoadArgs(UseCaseArgsBase):
    """User find args."""


@dataclass
class UserLoadResult(UseCaseResultBase):
    """User find result."""

    user: User
    user_score_overview: UserScoreOverview | None


class UserLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[UserLoadArgs, UserLoadResult]
):
    """The command for loading the current user."""

    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        super().__init__(auth_token_stamper, storage_engine)
        self._time_provider = time_provider

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: UserLoadArgs,
    ) -> UserLoadResult:
        """Execute the command's action."""
        score_overview = None
        if context.user.is_feature_available(UserFeature.GAMIFICATION):
            score_overview = await ScoreOverviewService().do_it(
                uow, context.user, self._time_provider.get_current_time()
            )
        return UserLoadResult(user=context.user, user_score_overview=score_overview)
