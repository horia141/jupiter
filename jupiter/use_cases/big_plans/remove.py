"""The command for removing a big plan."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase

LOGGER = logging.getLogger(__name__)


class BigPlanRemoveUseCase(UseCase['BigPlanRemoveUseCase.Args', None]):
    """The command for removing a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        BigPlanRemoveService(self._storage_engine, self._inbox_task_notion_manager, self._big_plan_notion_manager)\
            .remove(args.ref_id)
