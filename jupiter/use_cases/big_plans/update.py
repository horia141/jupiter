"""The command for updating a big plan."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanUpdateUseCase(UseCase['BigPlanUpdateUseCase.Args', None]):
    """The command for updating a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[BigPlanName]
        status: UpdateAction[BigPlanStatus]
        actionable_date: UpdateAction[Optional[ADate]]
        due_date: UpdateAction[Optional[ADate]]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider,
            storage_engine: StorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        should_change_name_on_notion_side = False

        with self._storage_engine.get_unit_of_work() as uow:
            big_plan = uow.big_plan_repository.load_by_id(args.ref_id)
            big_plan_collection = \
                uow.big_plan_collection_repository.load_by_id(big_plan.big_plan_collection_ref_id)

            if args.name.should_change:
                should_change_name_on_notion_side = True
                big_plan.change_name(args.name.value, self._time_provider.get_current_time())

            if args.status.should_change:
                big_plan.change_status(args.status.value, self._time_provider.get_current_time())

            if args.actionable_date.should_change:
                big_plan.change_actionable_date(args.actionable_date.value, self._time_provider.get_current_time())

            if args.due_date.should_change:
                big_plan.change_due_date(args.due_date.value, self._time_provider.get_current_time())

            uow.big_plan_repository.save(big_plan)

        notion_big_plan = self._big_plan_notion_manager.load_big_plan(
            big_plan.big_plan_collection_ref_id, big_plan.ref_id)
        notion_big_plan = notion_big_plan.join_with_aggregate_root(big_plan, None)
        self._big_plan_notion_manager.save_big_plan(big_plan.big_plan_collection_ref_id, notion_big_plan)

        if should_change_name_on_notion_side:
            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager)\
                .sync(big_plan_collection)

            with self._storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = \
                    uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_big_plan_ref_ids=[big_plan.ref_id])

                for inbox_task in all_inbox_tasks:
                    inbox_task.update_link_to_big_plan(big_plan.ref_id, self._time_provider.get_current_time())
                    uow.inbox_task_repository.save(inbox_task)
                    LOGGER.info(f'Updating the associated inbox task "{inbox_task.name}"')

            for inbox_task in all_inbox_tasks:
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = \
                    notion_inbox_task.join_with_aggregate_root(inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
