"""The command for updating a inbox task."""
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task import CannotModifyGeneratedTaskError
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class InboxTaskUpdateUseCase(UseCase['InboxTaskUpdateUseCase.Args', None]):
    """The command for updating a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[InboxTaskName]
        status: UpdateAction[InboxTaskStatus]
        eisen: UpdateAction[Eisen]
        difficulty: UpdateAction[Optional[Difficulty]]
        actionable_date: UpdateAction[Optional[ADate]]
        due_date: UpdateAction[Optional[ADate]]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)

            try:
                inbox_task = inbox_task.update(
                    name=args.name, status=args.status, eisen=args.eisen, difficulty=args.difficulty,
                    actionable_date=args.actionable_date, due_date=args.due_date,
                    source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            except CannotModifyGeneratedTaskError as err:
                raise InputValidationError(f"Modifing a generated task's field {err.field} is not possible") from err

            uow.inbox_task_repository.save(inbox_task)

            big_plan = None
            if inbox_task.big_plan_ref_id is not None:
                big_plan = uow.big_plan_repository.load_by_id(inbox_task.big_plan_ref_id)

        notion_inbox_task = \
            self._inbox_task_notion_manager.load_inbox_task(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
        notion_inbox_task = \
            notion_inbox_task.join_with_aggregate_root(
                inbox_task, NotionInboxTask.DirectInfo(big_plan.name if big_plan else None))
        self._inbox_task_notion_manager.save_inbox_task(inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
