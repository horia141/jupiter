"""Service for archiving a Slack task and associated entities."""
from typing import Final

from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class SlackTaskArchiveService:
    """Shared service for archiving a slack task."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ContextProgressReporter,
        slack_task: SlackTask,
    ) -> None:
        """Execute the service's action."""
        if slack_task.archived:
            return

        async with self._storage_engine.get_unit_of_work() as uow:
            slack_task_collection = (
                await uow.slack_task_collection_repository.load_by_id(
                    slack_task.slack_task_collection_ref_id,
                )
            )
            push_integration_group = (
                await uow.push_integration_group_repository.load_by_id(
                    slack_task_collection.push_integration_group_ref_id,
                )
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    push_integration_group.workspace_ref_id,
                )
            )

            inbox_tasks_to_archive = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=False,
                    filter_slack_task_ref_ids=[slack_task.ref_id],
                )
            )

        for inbox_task in inbox_tasks_to_archive:
            async with progress_reporter.start_archiving_entity(
                "inbox task",
                inbox_task.ref_id,
                str(inbox_task.name),
            ) as entity_reporter:
                async with self._storage_engine.get_unit_of_work() as uow:
                    inbox_task = inbox_task.mark_archived(
                        self._source,
                        self._time_provider.get_current_time(),
                    )
                    await uow.inbox_task_repository.save(inbox_task)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.start_archiving_entity(
            "Slack task",
            slack_task.ref_id,
            str(slack_task.simple_name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                slack_task = slack_task.mark_archived(
                    self._source,
                    self._time_provider.get_current_time(),
                )
                await uow.slack_task_repository.save(slack_task)
                await entity_reporter.mark_local_change()
