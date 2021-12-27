"""The command for associating a inbox task with a big plan."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.entity_name import EntityName
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskAssociateWithBigPlanUseCase(UseCase['InboxTaskAssociateWithBigPlanUseCase.Args', None]):
    """The command for associating a inbox task with a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        big_plan_ref_id: Optional[EntityId]

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]

    def __init__(
            self, time_provider: TimeProvider,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_engine: BigPlanEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        big_plan_name: Optional[EntityName] = None
        if args.big_plan_ref_id:
            with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
                big_plan = big_plan_uow.big_plan_repository.load_by_id(args.big_plan_ref_id)
            big_plan_name = big_plan.name

        with self._inbox_task_engine.get_unit_of_work() as uow:
            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)
            inbox_task.associate_with_big_plan(
                args.big_plan_ref_id, big_plan_name, self._time_provider.get_current_time())
            uow.inbox_task_repository.save(inbox_task)

        notion_inbox_task = \
            self._inbox_task_notion_manager.load_inbox_task(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
        notion_inbox_task = \
            notion_inbox_task.join_with_aggregate_root(inbox_task, NotionInboxTask.DirectInfo(big_plan_name))
        self._inbox_task_notion_manager.save_inbox_task(inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
