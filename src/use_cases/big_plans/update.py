"""The command for updating a big plan."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from domain.adate import ADate
from domain.big_plans.big_plan_status import BigPlanStatus
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from domain.entity_name import EntityName
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.inbox_tasks.service.big_plan_ref_options_update_service import InboxTaskBigPlanRefOptionsUpdateService
from domain.projects.infra.project_engine import ProjectEngine
from framework.update_action import UpdateAction
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanUpdateUseCase(UseCase['BigPlanUpdateUseCase.Args', None]):
    """The command for updating a big plan."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[EntityName]
        status: UpdateAction[BigPlanStatus]
        due_date: UpdateAction[Optional[ADate]]

    _time_provider: Final[TimeProvider]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, project_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        should_change_name_on_notion_side = False

        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan = big_plan_uow.big_plan_repository.load_by_id(args.ref_id)

            if args.name.should_change:
                should_change_name_on_notion_side = True
                big_plan.change_name(args.name.value, self._time_provider.get_current_time())

            if args.status.should_change:
                big_plan.change_status(args.status.value, self._time_provider.get_current_time())

            if args.due_date.should_change:
                big_plan.change_due_date(args.due_date.value, self._time_provider.get_current_time())

            big_plan_uow.big_plan_repository.save(big_plan)

        with self._project_engine.get_unit_of_work() as project_uow:
            project = project_uow.project_repository.load_by_id(big_plan.project_ref_id)

        notion_big_plan = self._big_plan_notion_manager.load_big_plan(big_plan.project_ref_id, big_plan.ref_id)
        notion_big_plan = notion_big_plan.join_with_aggregate_root(big_plan, None)
        self._big_plan_notion_manager.save_big_plan(big_plan.project_ref_id, notion_big_plan)

        if should_change_name_on_notion_side:
            InboxTaskBigPlanRefOptionsUpdateService(
                self._big_plan_engine, self._inbox_task_notion_manager).sync(project)

            with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                all_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_big_plan_ref_ids=[big_plan.ref_id])

                for inbox_task in all_inbox_tasks:
                    inbox_task.update_link_to_big_plan(big_plan.ref_id, self._time_provider.get_current_time())
                    inbox_task_uow.inbox_task_repository.save(inbox_task)
                    LOGGER.info(f'Updating the associated inbox task "{inbox_task.name}"')

            for inbox_task in all_inbox_tasks:
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(inbox_task.project_ref_id, inbox_task.ref_id)
                notion_inbox_task = \
                    notion_inbox_task.join_with_aggregate_root(inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(inbox_task.project_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
