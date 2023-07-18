"""The command for archiving a vacation."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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
class VacationArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class VacationArchiveUseCase(AppLoggedInMutationUseCase[VacationArchiveArgs, None]):
    """The command for archiving a vacation."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.VACATIONS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_archiving_entity(
            "vacation",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                (
                    await uow.vacation_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                vacation = await uow.vacation_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(vacation.name))

                vacation = vacation.mark_archived(
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.vacation_repository.save(vacation)
                await entity_reporter.mark_local_change()
