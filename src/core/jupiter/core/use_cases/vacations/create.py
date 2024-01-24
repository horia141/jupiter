"""The command for creating a vacation."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_name import VacationName
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

        vacation_collection = await uow.vacation_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        new_vacation = Vacation.new_vacation(
            context.domain_context,
            vacation_collection_ref_id=vacation_collection.ref_id,
            name=args.name,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        new_vacation = await uow.vacation_repository.create(new_vacation)
        await progress_reporter.mark_created(new_vacation)

        return VacationCreateResult(new_vacation=new_vacation)
