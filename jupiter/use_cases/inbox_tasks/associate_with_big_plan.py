"""The command for associating a inbox task with a big plan."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskAssociateWithBigPlanUseCase(UseCase['InboxTaskAssociateWithBigPlanUseCase.Args', None]):
    """The command for associating a inbox task with a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        big_plan_ref_id: Optional[EntityId]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider,
            storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        big_plan_name: Optional[BigPlanName] = None
        with self._storage_engine.get_unit_of_work() as uow:
            if args.big_plan_ref_id:
                big_plan = uow.big_plan_repository.load_by_id(args.big_plan_ref_id)
                big_plan_name = big_plan.name

            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)
            inbox_task = inbox_task.associate_with_big_plan(
                big_plan_ref_id=args.big_plan_ref_id, big_plan_name=big_plan_name,
                source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.inbox_task_repository.save(inbox_task)

        notion_inbox_task = \
            self._inbox_task_notion_manager.load_inbox_task(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
        notion_inbox_task = \
            notion_inbox_task.join_with_aggregate_root(inbox_task, NotionInboxTask.DirectInfo(big_plan_name))
        self._inbox_task_notion_manager.save_inbox_task(inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
