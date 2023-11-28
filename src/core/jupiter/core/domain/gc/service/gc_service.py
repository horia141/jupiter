"""Garbage collect a workspace."""

from typing import Final, Iterable, List, cast

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.service.archive_service import (
    EmailTaskArchiveService,
)
from jupiter.core.domain.push_integrations.slack.service.archive_service import (
    SlackTaskArchiveService,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainStorageEngine, DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class GCService:
    """Shared service for performing garbage collection."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _domain_storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        domain_storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._domain_storage_engine = domain_storage_engine

    async def do_it(
        self,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        gc_targets: list[SyncTarget],
    ) -> None:
        """Execute the service's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gc_log = await uow.gc_log_repository.load_by_parent(workspace.ref_id)
            gc_log_entry = GCLogEntry.new_log_entry(
                gc_log_ref_id=gc_log.ref_id,
                gc_targets=gc_targets,
                source=self._source,
                created_time=self._time_provider.get_current_time(),
            )
            gc_log_entry = await uow.gc_log_entry_repository.create(gc_log_entry)

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            big_plan_collection = (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            push_integration_group = (
                await uow.push_integration_group_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            slack_task_collection = (
                await uow.slack_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )

        if (
            workspace.is_feature_available(WorkspaceFeature.INBOX_TASKS)
            and SyncTarget.INBOX_TASKS in gc_targets
        ):
            async with progress_reporter.section("Inbox Tasks"):
                async with progress_reporter.section(
                    "Archiving all done inbox tasks",
                ):
                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        inbox_tasks = await uow.inbox_task_repository.find_all(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=False,
                        )
                    gc_log_entry = await self._archive_done_inbox_tasks(
                        progress_reporter,
                        inbox_tasks,
                        gc_log_entry,
                    )

        if (
            workspace.is_feature_available(WorkspaceFeature.BIG_PLANS)
            and SyncTarget.BIG_PLANS in gc_targets
        ):
            async with progress_reporter.section("Big Plans"):
                async with progress_reporter.section(
                    "Archiving all done big plans",
                ):
                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        big_plans = await uow.big_plan_repository.find_all(
                            parent_ref_id=big_plan_collection.ref_id,
                            allow_archived=False,
                        )
                gc_log_entry = await self._archive_done_big_plans(
                    uow,
                    progress_reporter,
                    big_plans,
                    gc_log_entry,
                )

        if (
            workspace.is_feature_available(WorkspaceFeature.SLACK_TASKS)
            and SyncTarget.SLACK_TASKS in gc_targets
        ):
            async with progress_reporter.section("Slack Tasks"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    slack_tasks = await uow.slack_task_repository.find_all(
                        parent_ref_id=slack_task_collection.ref_id,
                        allow_archived=False,
                    )
                    inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.SLACK_TASK],
                        filter_slack_task_ref_ids=[st.ref_id for st in slack_tasks],
                    )
                gc_log_entry = await self._archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
                    progress_reporter,
                    slack_tasks,
                    inbox_tasks,
                    gc_log_entry,
                )

        if (
            workspace.is_feature_available(WorkspaceFeature.EMAIL_TASKS)
            and SyncTarget.EMAIL_TASKS in gc_targets
        ):
            async with progress_reporter.section("Email Tasks"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    email_tasks = await uow.email_task_repository.find_all(
                        parent_ref_id=email_task_collection.ref_id,
                        allow_archived=False,
                    )
                    inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.EMAIL_TASK],
                        filter_email_task_ref_ids=[et.ref_id for et in email_tasks],
                    )
                gc_log_entry = await self._archive_email_tasks_whose_inbox_tasks_are_completed_or_archived(
                    progress_reporter,
                    email_tasks,
                    inbox_tasks,
                    gc_log_entry,
                )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            gc_log_entry = gc_log_entry.close(self._time_provider.get_current_time())
            gc_log_entry = await uow.gc_log_entry_repository.save(gc_log_entry)

    async def _archive_done_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        inbox_tasks: Iterable[InboxTask],
        gc_log_entry: GCLogEntry,
    ) -> GCLogEntry:
        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        )

        for inbox_task in inbox_tasks:
            if not inbox_task.status.is_completed:
                continue
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await inbox_task_archive_service.do_it(
                    uow, progress_reporter, inbox_task
                )
            gc_log_entry = gc_log_entry.add_entity(
                inbox_task,
                self._time_provider.get_current_time(),
            )

        return gc_log_entry

    async def _archive_done_big_plans(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        big_plans: Iterable[BigPlan],
        gc_log_entry: GCLogEntry,
    ) -> GCLogEntry:
        """Archive the done big plans."""
        big_plan_archive_service = BigPlanArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        )

        for big_plan in big_plans:
            if not big_plan.status.is_completed:
                continue
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                result = await big_plan_archive_service.do_it(
                    uow, progress_reporter, big_plan
                )

            gc_log_entry = gc_log_entry.add_entity(
                big_plan,
                self._time_provider.get_current_time(),
            )
            for archived_inbox_task in result.archived_inbox_tasks:
                gc_log_entry = gc_log_entry.add_entity(
                    archived_inbox_task,
                    self._time_provider.get_current_time(),
                )

        return gc_log_entry

    async def _archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
        self,
        progress_reporter: ProgressReporter,
        slack_tasks: List[SlackTask],
        inbox_tasks: List[InboxTask],
        gc_log_entry: GCLogEntry,
    ) -> GCLogEntry:
        slack_tasks_by_ref_id = {st.ref_id: st for st in slack_tasks}
        slack_task_arhive_service = SlackTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        )
        for inbox_task in inbox_tasks:
            if not (inbox_task.status.is_completed or inbox_task.archived):
                continue
            slack_task = slack_tasks_by_ref_id[
                cast(EntityId, inbox_task.slack_task_ref_id)
            ]
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                result = await slack_task_arhive_service.do_it(
                    uow,
                    progress_reporter,
                    slack_tasks_by_ref_id[cast(EntityId, inbox_task.slack_task_ref_id)],
                )

            gc_log_entry = gc_log_entry.add_entity(
                slack_task,
                self._time_provider.get_current_time(),
            )
            for archived_inbox_task in result.archived_inbox_tasks:
                gc_log_entry = gc_log_entry.add_entity(
                    archived_inbox_task,
                    self._time_provider.get_current_time(),
                )

        return gc_log_entry

    async def _archive_email_tasks_whose_inbox_tasks_are_completed_or_archived(
        self,
        progress_reporter: ProgressReporter,
        email_tasks: List[EmailTask],
        inbox_tasks: List[InboxTask],
        gc_log_entry: GCLogEntry,
    ) -> GCLogEntry:
        email_tasks_by_ref_id = {st.ref_id: st for st in email_tasks}
        email_task_arhive_service = EmailTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        )
        for inbox_task in inbox_tasks:
            if not (inbox_task.status.is_completed or inbox_task.archived):
                continue
            email_task = email_tasks_by_ref_id[
                cast(EntityId, inbox_task.email_task_ref_id)
            ]
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                result = await email_task_arhive_service.do_it(
                    uow,
                    progress_reporter,
                    email_task,
                )

            gc_log_entry = gc_log_entry.add_entity(
                email_task,
                self._time_provider.get_current_time(),
            )
            for archived_inbox_task in result.archived_inbox_tasks:
                gc_log_entry = gc_log_entry.add_entity(
                    archived_inbox_task,
                    self._time_provider.get_current_time(),
                )

        return gc_log_entry