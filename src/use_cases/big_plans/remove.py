"""The command for removing a big plan."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from domain.big_plans.service.remove_service import BigPlanRemoveService
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from models.framework import Command, EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanRemoveCommand(Command['BigPlanRemoveCommand.Args', None]):
    """The command for removing a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, big_plan_engine: BigPlanEngine,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        BigPlanRemoveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager, self._big_plan_engine,
            self._big_plan_notion_manager).remove(args.ref_id)
