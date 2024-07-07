"""The command for archiving a working mem."""

from jupiter.core.domain.concept.working_mem.working_mem import WorkingMem
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_archiver import generic_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class WorkingMemArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.WORKING_MEM)
class WorkingMemArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkingMemArchiveArgs, None]
):
    """The command for archiving a working mem."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkingMemArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        working_mem = await uow.get_for(WorkingMem).load_by_id(args.ref_id)
        if not working_mem.can_be_archived_at(self._time_provider.get_current_time()):
            raise Exception(
                "Cannot archive a working mem that is less than 14 days old."
            )
        await generic_archiver(
            context.domain_context, uow, progress_reporter, WorkingMem, args.ref_id
        )
