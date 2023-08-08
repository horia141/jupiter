"""The command for changing the project for a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
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
class BigPlanChangeProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    project_ref_id: Optional[EntityId] = None


class BigPlanChangeProjectUseCase(
    AppLoggedInMutationUseCase[BigPlanChangeProjectArgs, None]
):
    """The command for changing the project of a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return (Feature.BIG_PLANS, Feature.PROJECTS)

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanChangeProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            big_plan = await uow.big_plan_repository.load_by_id(args.ref_id)
            big_plan = big_plan.change_project(
                project_ref_id=args.project_ref_id or workspace.default_project_ref_id,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            await uow.big_plan_repository.save(big_plan)
            await progress_reporter.mark_updated(big_plan)

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_big_plan_ref_ids=[big_plan.ref_id],
            )

            for inbox_task in all_inbox_tasks:
                inbox_task = inbox_task.update_link_to_big_plan(
                    big_plan.project_ref_id,
                    big_plan.ref_id,
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.inbox_task_repository.save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)
