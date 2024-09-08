"""The command for updating a vacation's properties."""

from jupiter.core.domain.concept.vacations.vacation import Vacation
from jupiter.core.domain.concept.vacations.vacation_name import VacationName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class VacationUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[VacationName]
    start_date: UpdateAction[ADate]
    end_date: UpdateAction[ADate]


@mutation_use_case(WorkspaceFeature.VACATIONS)
class VacationUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[VacationUpdateArgs, None]
):
    """The command for updating a vacation's properties."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: VacationUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        vacation = await generic_loader(uow, Vacation, args.ref_id)

        vacation = vacation.update(
            context.domain_context,
            name=args.name,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        await uow.get_for(Vacation).save(vacation)
        await progress_reporter.mark_updated(vacation)
