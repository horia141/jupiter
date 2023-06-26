"""The command for creating a big plan."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class BigPlanCreateArgs(UseCaseArgsBase):
    """Big plan create args."""

    name: BigPlanName
    project_ref_id: Optional[EntityId] = None
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None


@dataclass
class BigPlanCreateResult(UseCaseResultBase):
    """Big plan create result."""

    new_big_plan: BigPlan


class BigPlanCreateUseCase(
    AppLoggedInMutationUseCase[BigPlanCreateArgs, BigPlanCreateResult]
):
    """The command for creating a big plan."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanCreateArgs,
    ) -> BigPlanCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_creating_entity(
            "big plan",
            str(args.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                big_plan_collection = (
                    await uow.big_plan_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )

                new_big_plan = BigPlan.new_big_plan(
                    big_plan_collection_ref_id=big_plan_collection.ref_id,
                    project_ref_id=args.project_ref_id
                    or workspace.default_project_ref_id,
                    archived=False,
                    name=args.name,
                    status=BigPlanStatus.ACCEPTED,
                    actionable_date=args.actionable_date,
                    due_date=args.due_date,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )
                new_big_plan = await uow.big_plan_repository.create(new_big_plan)
                await entity_reporter.mark_known_entity_id(new_big_plan.ref_id)
                await entity_reporter.mark_local_change()

        return BigPlanCreateResult(new_big_plan=new_big_plan)