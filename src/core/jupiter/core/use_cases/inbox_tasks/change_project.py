"""The command for changing the project for an inbox task ."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class InboxTaskChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


class InboxTaskChangeProjectUseCase(
    AppLoggedInMutationUseCase[InboxTaskChangeProjectArgs, None],
):
    """The command for changing the project of a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.INBOX_TASKS, Feature.PROJECTS)

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)

            try:
                inbox_task = inbox_task.change_project(
                    project_ref_id=args.project_ref_id
                    or workspace.default_project_ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
            except CannotModifyGeneratedTaskError as err:
                raise InputValidationError(
                    f"Modifying a generated task's field {err.field} is not possible",
                ) from err

            await uow.inbox_task_repository.save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)
