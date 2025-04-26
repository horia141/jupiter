"""Compute stats for a workspace."""

from typing import Final

from jupiter.core.domain.application.gamification.service.record_score_service import (
    RecordScoreService,
)
from jupiter.core.domain.application.report.service.report_service import ReportService
from jupiter.core.domain.application.stats.stats_log import StatsLog
from jupiter.core.domain.application.stats.stats_log_entry import StatsLogEntry
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan, BigPlanRepository
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.big_plans.big_plan_stats import (
    BigPlanStats,
    BigPlanStatsRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.journals.journal import Journal, JournalRepository
from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
from jupiter.core.domain.concept.journals.journal_stats import (
    JournalStats,
    JournalStatsRepository,
)
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.use_case import ProgressReporter


class StatsService:
    """Service for computing stats for a workspace."""

    _domain_storage_engine: Final[DomainStorageEngine]

    def __init__(self, domain_storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._domain_storage_engine = domain_storage_engine

    async def do_it(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        user: User,
        workspace: Workspace,
        today: ADate,
        stats_targets: list[SyncTarget],
        filter_habit_ref_ids: list[EntityId] | None = None,
        filter_big_plan_ref_ids: list[EntityId] | None = None,
        filter_journal_ref_ids: list[EntityId] | None = None,
    ) -> None:
        """Execute the service's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            stats_log = await uow.get_for(StatsLog).load_by_parent(workspace.ref_id)
            stats_log_entry = StatsLogEntry.new_log_entry(
                ctx,
                stats_log_ref_id=stats_log.ref_id,
                stats_targets=stats_targets,
                today=today,
            )
            stats_log_entry = await uow.get_for(StatsLogEntry).create(stats_log_entry)

            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(workspace.ref_id)
            big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
                workspace.ref_id
            )
            journal_collection = await uow.get_for(JournalCollection).load_by_parent(
                workspace.ref_id
            )

        if (
            workspace.is_feature_available(WorkspaceFeature.BIG_PLANS)
            and SyncTarget.BIG_PLANS in stats_targets
        ):
            async with progress_reporter.section("Computing stats for big plans"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_big_plans = await uow.get_for(BigPlan).find_all_generic(
                        parent_ref_id=big_plan_collection.ref_id,
                        allow_archived=False,
                        ref_id=(
                            filter_big_plan_ref_ids
                            if filter_big_plan_ref_ids
                            else NoFilter()
                        ),
                    )

                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        source=InboxTaskSource.BIG_PLAN,
                        source_entity_ref_id=(
                            [big_plan.ref_id for big_plan in all_big_plans]
                            if all_big_plans
                            else None  # This will find no inbox tasks if there are no big plans
                        ),
                    )

                stats_log_entry = await self._compute_stats_for_big_plans(
                    ctx,
                    user=user,
                    workspace=workspace,
                    progress_reporter=progress_reporter,
                    all_big_plans=all_big_plans,
                    all_inbox_tasks=all_inbox_tasks,
                    stats_log_entry=stats_log_entry,
                )

        if (
            workspace.is_feature_available(WorkspaceFeature.JOURNALS)
            and SyncTarget.JOURNALS in stats_targets
        ):
            async with progress_reporter.section("Computing stats for journals"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    if filter_journal_ref_ids:
                        all_journals = await uow.get(
                            JournalRepository
                        ).find_all_generic(
                            parent_ref_id=journal_collection.ref_id,
                            allow_archived=False,
                            ref_id=filter_journal_ref_ids,
                        )
                    else:
                        all_journals = await uow.get(
                            JournalRepository
                        ).find_all_in_range(
                            parent_ref_id=journal_collection.ref_id,
                            allow_archived=False,
                            filter_periods=list(p for p in RecurringTaskPeriod),
                            filter_start_date=today.subtract_days(400),
                            filter_end_date=today.add_days(30),
                        )

                stats_log_entry = await self._compute_stats_for_journals(
                    ctx,
                    user=user,
                    workspace=workspace,
                    progress_reporter=progress_reporter,
                    all_journals=all_journals,
                    stats_log_entry=stats_log_entry,
                )

        if (
            user.is_feature_available(UserFeature.GAMIFICATION)
            and SyncTarget.GAMIFICATION in stats_targets
        ):
            async with progress_reporter.section("Computing stats for gamification"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_inbox_tasks_last_year = await uow.get(
                        InboxTaskRepository
                    ).find_completed_in_range(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_include_sources=[s for s in InboxTaskSource],
                        filter_start_completed_date=today.subtract_days(365),
                        filter_end_completed_date=today,
                    )

                    all_big_plans_last_year = await uow.get(
                        BigPlanRepository
                    ).find_completed_in_range(
                        parent_ref_id=big_plan_collection.ref_id,
                        allow_archived=True,
                        filter_start_completed_date=today.subtract_days(365),
                        filter_end_completed_date=today,
                    )

                stats_log_entry = await self._compute_stats_for_gamification(
                    ctx,
                    user=user,
                    workspace=workspace,
                    progress_reporter=progress_reporter,
                    all_inbox_tasks_last_year=all_inbox_tasks_last_year,
                    all_big_plans_last_year=all_big_plans_last_year,
                    stats_log_entry=stats_log_entry,
                )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            stats_log_entry = stats_log_entry.close(ctx)
            await uow.get_for(StatsLogEntry).save(stats_log_entry)

    async def _compute_stats_for_big_plans(
        self,
        ctx: DomainContext,
        user: User,
        workspace: Workspace,
        progress_reporter: ProgressReporter,
        all_big_plans: list[BigPlan],
        all_inbox_tasks: list[InboxTask],
        stats_log_entry: StatsLogEntry,
    ) -> StatsLogEntry:
        # Group inbox tasks by big plan ref id
        inbox_tasks_by_big_plan_ref_id: dict[EntityId, list[InboxTask]] = {}
        for inbox_task in all_inbox_tasks:
            if inbox_task.source_entity_ref_id is None:
                continue
            if inbox_task.source_entity_ref_id not in inbox_tasks_by_big_plan_ref_id:
                inbox_tasks_by_big_plan_ref_id[inbox_task.source_entity_ref_id] = []
            inbox_tasks_by_big_plan_ref_id[inbox_task.source_entity_ref_id].append(
                inbox_task
            )

        # Compute stats for each big plan
        for big_plan in all_big_plans:
            inbox_tasks = inbox_tasks_by_big_plan_ref_id.get(big_plan.ref_id, [])
            all_inbox_tasks_cnt = len(inbox_tasks)
            completed_inbox_tasks_cnt = sum(
                1 for task in inbox_tasks if task.is_completed
            )

            new_big_plan_stats = BigPlanStats.new_stats_for_big_plan(
                ctx,
                big_plan_ref_id=big_plan.ref_id,
                all_inbox_tasks_cnt=all_inbox_tasks_cnt,
                completed_inbox_tasks_cnt=completed_inbox_tasks_cnt,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                new_big_plan_stats = await uow.get(BigPlanStatsRepository).save(
                    new_big_plan_stats
                )
            await progress_reporter.mark_updated(big_plan)
            stats_log_entry = stats_log_entry.add_entity_updated(ctx, big_plan)

        return stats_log_entry

    async def _compute_stats_for_journals(
        self,
        ctx: DomainContext,
        user: User,
        workspace: Workspace,
        progress_reporter: ProgressReporter,
        all_journals: list[Journal],
        stats_log_entry: StatsLogEntry,
    ) -> StatsLogEntry:
        report_service = ReportService(self._domain_storage_engine)

        for journal in all_journals:
            report_period_result = await report_service.do_it(
                user=user,
                workspace=workspace,
                today=journal.right_now,
                period=journal.period,
            )

            new_journal_stats = JournalStats.new_stats_for_journal(
                ctx,
                journal_ref_id=journal.ref_id,
                report=report_period_result,
            )

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                new_journal_stats = await uow.get(JournalStatsRepository).save(
                    new_journal_stats
                )
            await progress_reporter.mark_updated(journal)
            stats_log_entry = stats_log_entry.add_entity_updated(ctx, journal)

        return stats_log_entry

    async def _compute_stats_for_gamification(
        self,
        ctx: DomainContext,
        user: User,
        workspace: Workspace,
        progress_reporter: ProgressReporter,
        all_inbox_tasks_last_year: list[InboxTask],
        all_big_plans_last_year: list[BigPlan],
        stats_log_entry: StatsLogEntry,
    ) -> StatsLogEntry:
        record_score_service = RecordScoreService()
        for inbox_task in all_inbox_tasks_last_year:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                record_score_result = await record_score_service.record_task(
                    ctx,
                    uow,
                    user,
                    inbox_task,
                )
                if record_score_result is not None:
                    await progress_reporter.mark_updated(inbox_task)
                    stats_log_entry = stats_log_entry.add_entity_updated(
                        ctx, inbox_task
                    )

        for big_plan in all_big_plans_last_year:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                record_score_result = await record_score_service.record_task(
                    ctx,
                    uow,
                    user,
                    big_plan,
                )
                if record_score_result is not None:
                    await progress_reporter.mark_updated(big_plan)
                    stats_log_entry = stats_log_entry.add_entity_updated(ctx, big_plan)

        return stats_log_entry
