"""The command for associating a inbox task with a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class InboxTaskAssociateWithBigPlanArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    big_plan_ref_id: Optional[EntityId] = None


class InboxTaskAssociateWithBigPlanUseCase(
    AppLoggedInMutationUseCase[InboxTaskAssociateWithBigPlanArgs, None],
):
    """The command for associating a inbox task with a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.INBOX_TASKS, Feature.BIG_PLANS)

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskAssociateWithBigPlanArgs,
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
                    if args.big_plan_ref_id:
                        big_plan = await uow.big_plan_repository.load_by_id(
                            args.big_plan_ref_id,
                        )
                        inbox_task = inbox_task.associate_with_big_plan(
                            project_ref_id=big_plan.project_ref_id,
                            big_plan_ref_id=args.big_plan_ref_id,
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                    else:
                        inbox_task = inbox_task.release_from_big_plan(
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                except CannotModifyGeneratedTaskError as err:
                    raise InputValidationError(
                        f"Modifying a generated task's field {err.field} is not possible",
                    ) from err

                await uow.inbox_task_repository.save(inbox_task)
                await entity_reporter.mark_local_change()
