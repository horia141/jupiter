"""The command for updating a vacation's properties."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import Feature
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class VacationUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[VacationName]
    start_date: UpdateAction[ADate]
    end_date: UpdateAction[ADate]


class VacationUpdateUseCase(AppLoggedInMutationUseCase[VacationUpdateArgs, None]):
    """The command for updating a vacation's properties."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.VACATIONS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_updating_entity(
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

                vacation = vacation.update(
                    name=args.name,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await entity_reporter.mark_known_name(str(vacation.name))

                await uow.vacation_repository.save(vacation)
                await entity_reporter.mark_local_change()
