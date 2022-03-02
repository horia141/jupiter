"""The command for updating a big plan."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanUpdateUseCase(AppMutationUseCase['BigPlanUpdateUseCase.Args', None]):
    """The command for updating a big plan."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        name: UpdateAction[BigPlanName]
        status: UpdateAction[BigPlanStatus]
        actionable_date: UpdateAction[Optional[ADate]]
        due_date: UpdateAction[Optional[ADate]]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            big_plan = uow.big_plan_repository.load_by_id(args.ref_id)
            big_plan_collection = \
                uow.big_plan_collection_repository.load_by_id(big_plan.big_plan_collection_ref_id)
            project = uow.project_repository.load_by_id(big_plan.project_ref_id)

            big_plan = big_plan.update(
                name=args.name, status=args.status, actionable_date=args.actionable_date, due_date=args.due_date,
                source=EventSource.CLI, modification_time=self._time_provider.get_current_time())

            uow.big_plan_repository.save(big_plan)

        big_plan_direct_info = NotionBigPlan.DirectInfo(project_name=project.name)

        notion_big_plan = \
            self._big_plan_notion_manager.load_big_plan(big_plan.big_plan_collection_ref_id, big_plan.ref_id)
        notion_big_plan = notion_big_plan.join_with_entity(big_plan, big_plan_direct_info)
        self._big_plan_notion_manager.save_big_plan(big_plan.big_plan_collection_ref_id, notion_big_plan)

        if args.name.should_change:
            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager)\
                .sync(big_plan_collection)

            with self._storage_engine.get_unit_of_work() as uow:
                inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
                all_inbox_tasks = \
                    uow.inbox_task_repository.find_all(
                        inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True, filter_big_plan_ref_ids=[big_plan.ref_id])

                for inbox_task in all_inbox_tasks:
                    inbox_task = inbox_task.update_link_to_big_plan(
                        big_plan.project_ref_id, big_plan.ref_id, EventSource.CLI,
                        self._time_provider.get_current_time())
                    uow.inbox_task_repository.save(inbox_task)
                    LOGGER.info(f'Updating the associated inbox task "{inbox_task.name}"')

            for inbox_task in all_inbox_tasks:
                inbox_task_direct_info = \
                    NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=big_plan.name)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = \
                    notion_inbox_task.join_with_entity(inbox_task, inbox_task_direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
