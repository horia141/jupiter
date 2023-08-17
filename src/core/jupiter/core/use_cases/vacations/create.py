"""The command for creating a vacation."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
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
    AppTransactionalLoggedInMutationUseCase[VacationCreateArgs, VacationCreateResult],
):
    """The command for creating a vacation."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.VACATIONS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: VacationCreateArgs,
    ) -> VacationCreateResult:
        """Execute the command's actions."""
        workspace = context.workspace

        vacation_collection = await uow.vacation_collection_repository.load_by_parent(
            workspace.ref_id,
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
        await progress_reporter.mark_created(new_vacation)

        return VacationCreateResult(new_vacation=new_vacation)
