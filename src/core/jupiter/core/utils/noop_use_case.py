"""A use case that doesn't do anything."""
from dataclasses import dataclass

from jupiter.core.framework.use_case import UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class NoOpArgs(UseCaseArgsBase):
    """NoOp args."""


class NoOpUseCase(AppLoggedInReadonlyUseCase[NoOpArgs, None]):
    """A use case that doesn't do anything."""

    async def _execute(
        self, context: AppLoggedInUseCaseContext, args: NoOpArgs
    ) -> None:
        """Execute the command's actions."""
        return None
