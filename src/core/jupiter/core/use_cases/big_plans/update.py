"""The command for updating a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class BigPlanUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[BigPlanName]
    status: UpdateAction[BigPlanStatus]
    actionable_date: UpdateAction[Optional[ADate]]
    due_date: UpdateAction[Optional[ADate]]


class BigPlanUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanUpdateArgs, None]
):
    """The command for updating a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.BIG_PLANS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        big_plan = await uow.big_plan_repository.load_by_id(args.ref_id)

        big_plan = big_plan.update(
            name=args.name,
            status=args.status,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.big_plan_repository.save(big_plan)
        await progress_reporter.mark_updated(big_plan)
