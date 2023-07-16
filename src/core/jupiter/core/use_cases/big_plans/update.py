"""The command for updating a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    MarkProgressStatus,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class BigPlanUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[BigPlanName]
    status: UpdateAction[BigPlanStatus]
    actionable_date: UpdateAction[Optional[ADate]]
    due_date: UpdateAction[Optional[ADate]]


class BigPlanUpdateUseCase(AppLoggedInMutationUseCase[BigPlanUpdateArgs, None]):
    """The command for updating a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.BIG_PLANS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_updating_entity(
            "big plan",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                big_plan = await uow.big_plan_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(big_plan.name))

                big_plan = big_plan.update(
                    name=args.name,
                    status=args.status,
                    actionable_date=args.actionable_date,
                    due_date=args.due_date,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.big_plan_repository.save(big_plan)
                await entity_reporter.mark_local_change()

        if args.name.should_change:
            async with self._storage_engine.get_unit_of_work() as uow:
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
                async with progress_reporter.start_updating_entity(
                    "inbox task",
                    inbox_task.ref_id,
                    str(inbox_task.name),
                ) as entity_reporter:
                    async with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task = inbox_task.update_link_to_big_plan(
                            big_plan.project_ref_id,
                            big_plan.ref_id,
                            EventSource.CLI,
                            self._time_provider.get_current_time(),
                        )
                        await entity_reporter.mark_known_name(str(inbox_task.name))
                        await uow.inbox_task_repository.save(inbox_task)
                        await entity_reporter.mark_local_change()

                    if inbox_task.archived:
                        await entity_reporter.mark_remote_change(
                            success=MarkProgressStatus.NOT_NEEDED,
                        )
                        continue
