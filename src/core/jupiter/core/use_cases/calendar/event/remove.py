"""Use case for removing a calendar event."""
from jupiter.core.domain.calendar.calendar_event import CalendarEvent
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra import generic_remover
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class CalendarEventRemoveArgs(UseCaseArgsBase):
    """CalendarEventRemove args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CALENDARS)
class CalendarEventRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[CalendarEventRemoveArgs, None]
):
    """The command for removing a calendar event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_remover(
            context.domain_context, uow, progress_reporter, CalendarEvent, args.ref_id
        )