"""Shared module for removing a big plan."""
from typing import Final

from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter


class BigPlanRemoveService:
    """Shared service for removing a big plan."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def remove(
        self,
        reporter: ProgressReporter,
        workspace: Workspace,
        ref_id: EntityId,
    ) -> None:
        """Hard remove a big plan."""
        async with self._storage_engine.get_unit_of_work() as uow:
            (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            big_plan = await uow.big_plan_repository.load_by_id(
                ref_id,
                allow_archived=True,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            inbox_tasks_to_remove = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_big_plan_ref_ids=[ref_id],
                )
            )

            for inbox_task in inbox_tasks_to_remove:
                await uow.inbox_task_repository.remove(inbox_task.ref_id)
                await reporter.mark_removed(inbox_task)

            big_plan = await uow.big_plan_repository.remove(ref_id)
            await reporter.mark_removed(big_plan)
