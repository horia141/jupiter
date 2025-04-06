"""Use case for creating a schedule stream."""

from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.schedule.schedule_stream_color import (
    ScheduleStreamColor,
)
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter
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
class ScheduleStreamCreateForUserArgs(UseCaseArgsBase):
    """Args."""

    name: ScheduleStreamName
    color: ScheduleStreamColor


@use_case_result
class ScheduleStreamCreateForUserResult(UseCaseResultBase):
    """Result."""

    new_schedule_stream: ScheduleStream


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleStreamCreateForUserUseCase(
    AppTransactionalLoggedInMutationUseCase[
        ScheduleStreamCreateForUserArgs, ScheduleStreamCreateForUserResult
    ]
):
    """Use case for creating a schedule stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleStreamCreateForUserArgs,
    ) -> ScheduleStreamCreateForUserResult:
        """Perform the transactional mutation."""
        workspace = context.workspace
        schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
            workspace.ref_id
        )
        schedule_stream = ScheduleStream.new_schedule_stream_for_user(
            context.domain_context,
            schedule_domain_ref_id=schedule_domain.ref_id,
            name=args.name,
            color=args.color,
        )
        schedule_stream = await generic_creator(uow, progress_reporter, schedule_stream)
        return ScheduleStreamCreateForUserResult(new_schedule_stream=schedule_stream)
