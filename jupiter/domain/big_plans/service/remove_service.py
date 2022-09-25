"""Shared module for removing a big plan."""
import logging
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import (
    BigPlanNotionManager,
    NotionBigPlanNotFoundError,
)
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
    NotionInboxTaskNotFoundError,
)
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service import (
    InboxTaskBigPlanRefOptionsUpdateService,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

LOGGER = logging.getLogger(__name__)


class BigPlanRemoveService:
    """Shared service for removing a big plan."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        big_plan_notion_manager: BigPlanNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def remove(
        self, reporter: ProgressReporter, workspace: Workspace, ref_id: EntityId
    ) -> None:
        """Hard remove a big plan."""
        with self._storage_engine.get_unit_of_work() as uow:
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plan = uow.big_plan_repository.load_by_id(ref_id, allow_archived=True)
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            inbox_tasks_to_remove = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_big_plan_ref_ids=[ref_id],
            )

        for inbox_task in inbox_tasks_to_remove:
            with reporter.start_removing_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.remove(inbox_task.ref_id)
                    entity_reporter.mark_local_change()

                try:
                    self._inbox_task_notion_manager.remove_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionInboxTaskNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping removal on Notion side because inbox task was not found"
                    )
                    entity_reporter.mark_remote_change(
                        success=MarkProgressStatus.FAILED
                    )

        with reporter.start_removing_entity(
            "big plan", ref_id, str(big_plan.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                big_plan = uow.big_plan_repository.remove(ref_id)
            entity_reporter.mark_local_change()

            try:
                self._big_plan_notion_manager.remove_leaf(
                    big_plan.big_plan_collection_ref_id, big_plan.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionBigPlanNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because big plan was not found"
                )
                entity_reporter.mark_remote_change(success=MarkProgressStatus.FAILED)

            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager
            ).sync(big_plan_collection)
            entity_reporter.mark_other_progress("inbox-task-refs")
