"""The command for creating a vacation."""

from jupiter.core.domain.concept.vacations.vacation import Vacation
from jupiter.core.domain.concept.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.concept.vacations.vacation_name import VacationName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class VacationCreateArgs(UseCaseArgsBase):
    """Vacation creation parameters."""

    name: VacationName
    start_date: ADate
    end_date: ADate


@use_case_result
class VacationCreateResult(UseCaseResultBase):
    """Vacation creation result."""

    new_vacation: Vacation
    new_time_event_block: TimeEventFullDaysBlock


@mutation_use_case(WorkspaceFeature.VACATIONS)
class VacationCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[VacationCreateArgs, VacationCreateResult],
):
    """The command for creating a vacation."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: VacationCreateArgs,
    ) -> VacationCreateResult:
        """Execute the command's actions."""
        workspace = context.workspace

        vacation_collection = await uow.get_for(VacationCollection).load_by_parent(
            workspace.ref_id,
        )
        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id,
        )

        new_vacation = Vacation.new_vacation(
            context.domain_context,
            vacation_collection_ref_id=vacation_collection.ref_id,
            name=args.name,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        new_vacation = await uow.get_for(Vacation).create(new_vacation)
        await progress_reporter.mark_created(new_vacation)

        new_time_event_block = TimeEventFullDaysBlock.new_time_event_for_vacation(
            context.domain_context,
            time_event_domain_ref_id=time_event_domain.ref_id,
            vacation_ref_id=new_vacation.ref_id,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        await uow.get_for(TimeEventFullDaysBlock).create(new_time_event_block)

        return VacationCreateResult(
            new_vacation=new_vacation, new_time_event_block=new_time_event_block
        )
