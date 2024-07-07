"""The command for updating a inbox task."""

from jupiter.core.domain.application.gamification.service.record_score_service import (
    RecordScoreResult,
    RecordScoreService,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    CannotModifyGeneratedTaskError,
    InboxTask,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
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
class InboxTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[InboxTaskName]
    status: UpdateAction[InboxTaskStatus]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Difficulty | None]
    actionable_date: UpdateAction[ADate | None]
    due_date: UpdateAction[ADate | None]


@use_case_result
class InboxTaskUpdateResult(UseCaseResultBase):
    """InboxTaskUpdate result."""

    record_score_result: RecordScoreResult | None


@mutation_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskUpdateArgs, InboxTaskUpdateResult]
):
    """The command for updating a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskUpdateArgs,
    ) -> InboxTaskUpdateResult:
        """Execute the command's action."""
        inbox_task = await uow.get_for(InboxTask).load_by_id(args.ref_id)

        try:
            inbox_task = inbox_task.update(
                ctx=context.domain_context,
                name=args.name,
                status=args.status,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
            )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifing a generated task's field {err.field} is not possible",
            ) from err

        await uow.get_for(InboxTask).save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)

        record_score_result = None
        if context.user.is_feature_available(UserFeature.GAMIFICATION):
            record_score_result = await RecordScoreService().record_task(
                context.domain_context, uow, context.user, inbox_task
            )

        return InboxTaskUpdateResult(record_score_result=record_score_result)
