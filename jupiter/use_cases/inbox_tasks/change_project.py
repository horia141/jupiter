"""The command for changing the project for an inbox task ."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskChangeProjectUseCase(AppMutationUseCase['InboxTaskChangeProjectUseCase.Args', None]):
    """The command for changing the project of a inbox task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        project_key: Optional[ProjectKey]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)

            if args.project_key:
                project = uow.project_repository.load_by_key(project_collection.ref_id, args.project_key)
            else:
                project = uow.project_repository.load_by_id(workspace.default_project_ref_id)

            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)

            try:
                inbox_task = \
                    inbox_task.change_project(
                        project_ref_id=project.ref_id, source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())
            except CannotModifyGeneratedTaskError as err:
                raise InputValidationError(f"Modifying a generated task's field {err.field} is not possible") from err

            uow.inbox_task_repository.save(inbox_task)

            big_plan_name = None
            if inbox_task.big_plan_ref_id is not None:
                big_plan_name = uow.big_plan_repository.load_by_id(inbox_task.big_plan_ref_id).name

        direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=big_plan_name)
        notion_inbox_task = \
            self._inbox_task_notion_manager.load_inbox_task(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
        notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
        self._inbox_task_notion_manager.save_inbox_task(inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
