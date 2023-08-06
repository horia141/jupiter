"""The command for updating a inbox task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
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


class InboxTaskUpdateUseCase(AppLoggedInMutationUseCase[InboxTaskUpdateArgs, None]):
    """The command for updating a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.INBOX_TASKS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "inbox task",
            args.ref_id,
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(inbox_task.name))

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
                await entity_reporter.mark_local_change()
