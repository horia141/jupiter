"""Shared logic for archiving a big plan."""
from typing import Final

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class BigPlanArchiveService:
    """Shared logic for archiving a big plan."""

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
        big_plan: BigPlan,
    ) -> None:
        """Execute the service's action."""
        if big_plan.archived:
            return

        async with self._storage_engine.get_unit_of_work() as uow:
            big_plan_collection = await uow.big_plan_collection_repository.load_by_id(
                big_plan.big_plan_collection_ref_id,
            )

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    big_plan_collection.workspace_ref_id,
                )
            )
            inbox_tasks_to_archive = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=False,
                    filter_big_plan_ref_ids=[big_plan.ref_id],
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
            "big plan",
            big_plan.ref_id,
            str(big_plan.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                big_plan = big_plan.mark_archived(
                    self._source,
                    self._time_provider.get_current_time(),
                )
                await uow.big_plan_repository.save(big_plan)
                await entity_reporter.mark_local_change()
