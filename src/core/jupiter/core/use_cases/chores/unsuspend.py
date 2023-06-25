"""The command for unsuspending a chore."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ChoreUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class ChoreUnsuspendUseCase(AppLoggedInMutationUseCase[ChoreUnsuspendArgs, None]):
    """The command for unsuspending a chore."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "chore",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                chore = await uow.chore_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(chore.name))
                chore = chore.unsuspend(
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await uow.chore_repository.save(chore)
                await entity_reporter.mark_local_change()
