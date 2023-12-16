"""The command for updating a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.gamification.service.record_score_service import (
    RecordScoreResult,
    RecordScoreService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
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


@dataclass
class BigPlanUpdateResult(UseCaseResultBase):
    """InboxTaskUpdate result."""

    record_score_result: RecordScoreResult | None = None


class BigPlanUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanUpdateArgs, BigPlanUpdateResult]
):
    """The command for updating a big plan."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.BIG_PLANS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: BigPlanUpdateArgs,
    ) -> BigPlanUpdateResult:
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

        record_score_result = None
        if context.user.is_feature_available(UserFeature.GAMIFICATION):
            record_score_result = await RecordScoreService(
                EventSource.CLI, self._time_provider
            ).record_task(uow, context.user, big_plan)

        return BigPlanUpdateResult(record_score_result=record_score_result)
