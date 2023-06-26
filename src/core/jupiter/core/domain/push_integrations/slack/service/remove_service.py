"""Service for hard removing a Slack task and associated inbox task."""
from typing import Final

from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.use_case import ContextProgressReporter


class SlackTaskRemoveService:
    """Shared service for hard removing a slack task."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ContextProgressReporter,
        slack_task: SlackTask,
    ) -> None:
        """Execute the service's action."""
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
            inbox_tasks_to_remove = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_slack_task_ref_ids=[slack_task.ref_id],
                )
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine,
        )
        for inbox_task in inbox_tasks_to_remove:
            await inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        async with progress_reporter.start_removing_entity(
            "slack task",
            slack_task.ref_id,
            str(slack_task.simple_name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                await uow.slack_task_repository.remove(slack_task.ref_id)
                await entity_reporter.mark_local_change()