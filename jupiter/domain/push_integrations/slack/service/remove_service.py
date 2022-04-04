"""Service for hard removing a Slack task and associated inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import SlackTaskNotionManager, \
    NotionSlackTaskNotFoundError
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.storage_engine import DomainStorageEngine

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
            slack_task_notion_manager: SlackTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._slack_task_notion_manager = slack_task_notion_manager

    def do_it(self, slack_task: SlackTask) -> None:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            uow.slack_task_repository.remove(slack_task.ref_id)

            slack_task_collection = \
                uow.slack_task_collection_repository.load_by_id(slack_task.slack_task_collection_ref_id)
            push_integration_group = \
                uow.push_integration_group_repository.load_by_id(slack_task_collection.push_integration_group_ref_id)
            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_parent(push_integration_group.workspace_ref_id)

            inbox_tasks_to_archive = \
                uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id, allow_archived=False,
                    filter_slack_task_ref_ids=[slack_task.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                uow.inbox_task_repository.remove(inbox_task.ref_id)

        try:
            self._slack_task_notion_manager.remove_leaf(
                slack_task.slack_task_collection_ref_id, slack_task.ref_id)
        except NotionSlackTaskNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping archival on Notion side because habit was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_leaf(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping archival on Notion side because inbox task was not found")
