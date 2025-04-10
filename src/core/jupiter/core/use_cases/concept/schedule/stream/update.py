"""Use case for updating a schedule stream."""

from jupiter.core.domain.concept.schedule.schedule_stream import (
    ScheduleStream,
)
from jupiter.core.domain.concept.schedule.schedule_stream_color import (
    ScheduleStreamColor,
)
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ScheduleStreamUpdateArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    name: UpdateAction[ScheduleStreamName]
    color: UpdateAction[ScheduleStreamColor]


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleStreamUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ScheduleStreamUpdateArgs, None]
):
    """Use case for updating a schedule stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleStreamUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        schedule_stream = await uow.get_for(ScheduleStream).load_by_id(args.ref_id)

        if (
            args.name.should_change
            and args.name.just_the_value != schedule_stream.name
            and not schedule_stream.can_be_modified_independently
        ):
            raise InputValidationError(
                "The name of this schedule stream cannot be changed."
            )

        schedule_stream = schedule_stream.update(
            context.domain_context,
            name=args.name,
            color=args.color,
        )

        await uow.get_for(ScheduleStream).save(schedule_stream)
        await progress_reporter.mark_updated(schedule_stream)
