"""The command for finding a recurring task."""
from dataclasses import dataclass
from typing import Iterable, Optional, Final, List

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.projects.infra.project_engine import ProjectEngine
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase


class RecurringTaskFindUseCase(UseCase['RecurringTaskFindUseCase.Args', 'RecurringTaskFindUseCase.Result']):
    """The command for finding a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        show_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass()
    class ResultEntry:
        """A single entry in the load all recurring tasks response."""
        recurring_task: RecurringTask
        inbox_tasks: Iterable[InboxTask]

    @dataclass()
    class Result:
        """The result."""
        recurring_tasks: Iterable['RecurringTaskFindUseCase.ResultEntry']

    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _recurring_task_engine: Final[RecurringTaskEngine]

    def __init__(
            self, project_engine: ProjectEngine, inbox_task_engine: InboxTaskEngine,
            recurring_task_engine: RecurringTaskEngine) -> None:
        """Constructor."""
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._recurring_task_engine = recurring_task_engine

    def execute(self, args: Args) -> 'Result':
        """Execute the command's action."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if args.filter_project_keys:
            with self._project_engine.get_unit_of_work() as project_uow:
                projects = project_uow.project_repository.find_all(filter_keys=args.filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            recurring_task_collections = \
                recurring_task_uow.recurring_task_collection_repository.find_all(
                    filter_project_ref_ids=filter_project_ref_ids)
            recurring_tasks = recurring_task_uow.recurring_task_repository.find_all(
                allow_archived=args.show_archived, filter_ref_ids=args.filter_ref_ids,
                filter_recurring_task_collection_ref_ids=[rct.ref_id for rct in recurring_task_collections])
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                allow_archived=True, filter_recurring_task_ref_ids=(bp.ref_id for bp in recurring_tasks))

        return RecurringTaskFindUseCase.Result(
            recurring_tasks=[
                RecurringTaskFindUseCase.ResultEntry(
                    recurring_task=rt,
                    inbox_tasks=[it for it in inbox_tasks if it.recurring_task_ref_id == rt.ref_id])
                for rt in recurring_tasks])
