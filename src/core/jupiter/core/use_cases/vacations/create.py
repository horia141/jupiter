"""The command for creating a vacation."""
from dataclasses import dataclass

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class VacationCreateArgs(UseCaseArgsBase):
    """Vacation creation parameters."""

    name: VacationName
    start_date: ADate
    end_date: ADate


@dataclass
class VacationCreateResult(UseCaseResultBase):
    """Vacation creation result."""

    new_vacation: Vacation


class VacationCreateUseCase(
    AppLoggedInMutationUseCase[VacationCreateArgs, VacationCreateResult],
):
    """The command for creating a vacation."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationCreateArgs,
    ) -> VacationCreateResult:
        """Execute the command's actions."""
        workspace = context.workspace

        async with progress_reporter.start_creating_entity(
            "vacation",
            str(args.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                vacation_collection = (
                    await uow.vacation_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )

                new_vacation = Vacation.new_vacation(
                    archived=False,
                    vacation_collection_ref_id=vacation_collection.ref_id,
                    name=args.name,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                new_vacation = await uow.vacation_repository.create(new_vacation)
                await entity_reporter.mark_known_entity_id(new_vacation.ref_id)
                await entity_reporter.mark_local_change()

        return VacationCreateResult(new_vacation=new_vacation)
