"""Service for hard removing a Slack task and associated inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
    NotionSlackTaskNotFoundError,
)
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

LOGGER = logging.getLogger(__name__)


class SlackTaskRemoveService:
    """Shared service for hard removing a slack task."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _slack_task_notion_manager: Final[SlackTaskNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        slack_task_notion_manager: SlackTaskNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._slack_task_notion_manager = slack_task_notion_manager

    def do_it(self, progress_reporter: ProgressReporter, slack_task: SlackTask) -> None:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            slack_task_collection = uow.slack_task_collection_repository.load_by_id(
                slack_task.slack_task_collection_ref_id
            )
            push_integration_group = uow.push_integration_group_repository.load_by_id(
                slack_task_collection.push_integration_group_ref_id
            )
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                push_integration_group.workspace_ref_id
            )
            inbox_tasks_to_remove = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_slack_task_ref_ids=[slack_task.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in inbox_tasks_to_remove:
            inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        with progress_reporter.start_removing_entity(
            "slack task", slack_task.ref_id, str(slack_task.simple_name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                uow.slack_task_repository.remove(slack_task.ref_id)
                entity_reporter.mark_local_change()

            try:
                self._slack_task_notion_manager.remove_leaf(
                    slack_task.slack_task_collection_ref_id, slack_task.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionSlackTaskNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because habit was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
