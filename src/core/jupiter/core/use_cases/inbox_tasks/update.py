"""The command for updating a inbox task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class InboxTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[InboxTaskName]
    status: UpdateAction[InboxTaskStatus]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Optional[Difficulty]]
    actionable_date: UpdateAction[Optional[ADate]]
    due_date: UpdateAction[Optional[ADate]]


class InboxTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskUpdateArgs, None]
):
    """The command for updating a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.INBOX_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)

        try:
            inbox_task = inbox_task.update(
                name=args.name,
                status=args.status,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifing a generated task's field {err.field} is not possible",
            ) from err

        await uow.inbox_task_repository.save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)
