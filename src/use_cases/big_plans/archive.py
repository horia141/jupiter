"""The command for archiving a big plan."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager, NotionBigPlanNotFoundError
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from domain.inbox_tasks.service.big_plan_ref_options_update_service import InboxTaskBigPlanRefOptionsUpdateService
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanArchiveUseCase(UseCase['BigPlanArchiveUseCase.Args', None]):
    """The command for archiving a big plan."""

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
            self, time_provider: TimeProvider,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_tasks_for_big_plan = inbox_task_uow.inbox_task_repository.find_all(
                filter_big_plan_ref_ids=[args.ref_id])

        inbox_task_archive_service = \
            InboxTaskArchiveService(self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
        for inbox_task in inbox_tasks_for_big_plan:
            LOGGER.info(f"Archiving task {inbox_task.name} for plan")
            inbox_task_archive_service.do_it(inbox_task)
        LOGGER.info("Archived all tasks")

        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan = big_plan_uow.big_plan_repository.load_by_id(args.ref_id)
            big_plan_collection = \
                big_plan_uow.big_plan_collection_repository.load_by_id(big_plan.big_plan_collection_ref_id)
            big_plan.mark_archived(self._time_provider.get_current_time())
            big_plan_uow.big_plan_repository.save(big_plan)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        try:
            self._big_plan_notion_manager.remove_big_plan(big_plan.big_plan_collection_ref_id, args.ref_id)
            LOGGER.info("Applied Notion changes")
        except NotionBigPlanNotFoundError:
            LOGGER.info("Skipping archiving of Notion inbox task because it could not be found")

        LOGGER.info(f"Archived the big plan")

        InboxTaskBigPlanRefOptionsUpdateService(
            self._big_plan_engine, self._inbox_task_engine, self._inbox_task_notion_manager).sync(big_plan_collection)
        LOGGER.info(f"Updated the schema for the associated inbox")
