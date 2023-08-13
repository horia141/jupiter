"""The command for updating a user's properties."""
from dataclasses import dataclass

from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class UserUpdateArgs(UseCaseArgsBase):
    """User update args."""

    name: UpdateAction[UserName]
    timezone: UpdateAction[Timezone]


class UserUpdateUseCase(AppLoggedInMutationUseCase[UserUpdateArgs, None]):
    """The command for updating a user's properties."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UserUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            user = context.user.update(
                name=args.name,
                timezone=args.timezone,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )
            await uow.user_repository.save(user)
