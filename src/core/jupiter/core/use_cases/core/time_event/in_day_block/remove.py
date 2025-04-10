"""Use case for removing the in day event."""

from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class TimeEventInDayBlockRemoveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case()
class TimeEventInDayBlockRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[TimeEventInDayBlockRemoveArgs, None]
):
    """Use case for removing the in day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimeEventInDayBlockRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        time_event_block = await uow.get_for(TimeEventInDayBlock).load_by_id(
            args.ref_id
        )
        if not time_event_block.can_be_modified_independently:
            raise InputValidationError("Cannot archive a linked task")
        await generic_crown_remover(
            context.domain_context,
            uow,
            progress_reporter,
            TimeEventInDayBlock,
            args.ref_id,
        )
