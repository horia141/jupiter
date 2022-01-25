"""The command for finding a recurring task."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class RecurringTaskFindUseCase(AppReadonlyUseCase['RecurringTaskFindUseCase.Args', 'RecurringTaskFindUseCase.Result']):
    """The command for finding a recurring task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        show_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single entry in the load all recurring tasks response."""
        recurring_task: RecurringTask
        inbox_tasks: Iterable[InboxTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """The result."""
        recurring_tasks: Iterable['RecurringTaskFindUseCase.ResultEntry']

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'Result':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            filter_project_ref_ids: Optional[List[EntityId]] = None
            if args.filter_project_keys:
                projects = uow.project_repository.find_all(filter_keys=args.filter_project_keys)
                filter_project_ref_ids = [p.ref_id for p in projects]

            recurring_task_collections = \
                uow.recurring_task_collection_repository.find_all(
                    filter_project_ref_ids=filter_project_ref_ids)
            recurring_tasks = uow.recurring_task_repository.find_all(
                allow_archived=args.show_archived, filter_ref_ids=args.filter_ref_ids,
                filter_recurring_task_collection_ref_ids=[rct.ref_id for rct in recurring_task_collections])

            inbox_tasks = uow.inbox_task_repository.find_all(
                allow_archived=True, filter_recurring_task_ref_ids=(bp.ref_id for bp in recurring_tasks))

        return RecurringTaskFindUseCase.Result(
            recurring_tasks=[
                RecurringTaskFindUseCase.ResultEntry(
                    recurring_task=rt,
                    inbox_tasks=[it for it in inbox_tasks if it.recurring_task_ref_id == rt.ref_id])
                for rt in recurring_tasks])
