"""The command for generating new tasks."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.gen.service.gen_service import GenService
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.sync_target import SyncTarget
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
class GenDoArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    source: EventSource
    gen_even_if_not_modified: bool
    today: Optional[ADate] = None
    gen_targets: Optional[List[SyncTarget]] = None
    period: Optional[List[RecurringTaskPeriod]] = None
    filter_project_ref_ids: Optional[List[EntityId]] = None
    filter_habit_ref_ids: Optional[List[EntityId]] = None
    filter_chore_ref_ids: Optional[List[EntityId]] = None
    filter_metric_ref_ids: Optional[List[EntityId]] = None
    filter_person_ref_ids: Optional[List[EntityId]] = None
    filter_slack_task_ref_ids: Optional[List[EntityId]] = None
    filter_email_task_ref_ids: Optional[List[EntityId]] = None


class GenDoUseCase(AppLoggedInMutationUseCase[GenDoArgs, None]):
    """The command for generating new tasks."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: GenDoArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace
        today = args.today or self._time_provider.get_current_date()

        gen_targets = (
            args.gen_targets
            if args.gen_targets is not None
            else workspace.infer_sync_targets_for_enabled_features(None)
        )

        gen_service = GenService(
            source=args.source,
            time_provider=self._time_provider,
            domain_storage_engine=self._domain_storage_engine,
        )

        await gen_service.do_it(
            progress_reporter=progress_reporter,
            user=user,
            workspace=workspace,
            gen_even_if_not_modified=args.gen_even_if_not_modified,
            today=today,
            gen_targets=gen_targets,
            period=args.period,
            filter_project_ref_ids=args.filter_project_ref_ids,
            filter_habit_ref_ids=args.filter_habit_ref_ids,
            filter_chore_ref_ids=args.filter_chore_ref_ids,
            filter_metric_ref_ids=args.filter_metric_ref_ids,
            filter_person_ref_ids=args.filter_person_ref_ids,
            filter_slack_task_ref_ids=args.filter_slack_task_ref_ids,
            filter_email_task_ref_ids=args.filter_email_task_ref_ids,
        )
