"""The command for finding a inbox task."""
from dataclasses import dataclass
from typing import Optional, Iterable, List

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.chores.chore import Chore
from jupiter.domain.habits.habit import Habit
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.persons.person import Person
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class InboxTaskFindUseCase(
    AppReadonlyUseCase["InboxTaskFindUseCase.Args", "InboxTaskFindUseCase.Result"]
):
    """The command for finding a inbox task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        allow_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_sources: Optional[Iterable[InboxTaskSource]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single entry in the load all inbox tasks response."""

        inbox_task: InboxTask
        project: Project
        habit: Optional[Habit]
        chore: Optional[Chore]
        big_plan: Optional[BigPlan]
        metric: Optional[Metric]
        person: Optional[Person]
        slack_task: Optional[SlackTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result."""

        inbox_tasks: Iterable["InboxTaskFindUseCase.ResultEntry"]

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            filter_project_ref_ids: Optional[List[EntityId]]
            if args.filter_project_keys:
                projects = uow.project_repository.find_all_with_filters(
                    parent_ref_id=project_collection.ref_id,
                    filter_keys=args.filter_project_keys,
                )
                filter_project_ref_ids = [p.ref_id for p in projects]
            else:
                projects = uow.project_repository.find_all(
                    parent_ref_id=project_collection.ref_id
                )
                filter_project_ref_ids = None
            project_by_ref_id = {p.ref_id: p for p in projects}

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            habit_collection = uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                workspace.ref_id
            )
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            person_collection = uow.person_collection_repository.load_by_parent(
                workspace.ref_id
            )
            push_integrations_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            slack_task_collection = uow.slack_task_collection_repository.load_by_parent(
                push_integrations_group.ref_id
            )

            inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
                filter_sources=args.filter_sources,
                filter_project_ref_ids=filter_project_ref_ids,
            )

            habits = uow.habit_repository.find_all(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.habit_ref_id for it in inbox_tasks if it.habit_ref_id is not None
                ),
            )
            habits_by_ref_id = {rt.ref_id: rt for rt in habits}

            chores = uow.chore_repository.find_all(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.chore_ref_id for it in inbox_tasks if it.chore_ref_id is not None
                ),
            )
            chores_by_ref_id = {rt.ref_id: rt for rt in chores}

            big_plans = uow.big_plan_repository.find_all(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.big_plan_ref_id
                    for it in inbox_tasks
                    if it.big_plan_ref_id is not None
                ),
            )
            big_plans_by_ref_id = {bp.ref_id: bp for bp in big_plans}

            metrics = uow.metric_repository.find_all(
                parent_ref_id=metric_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.metric_ref_id
                    for it in inbox_tasks
                    if it.metric_ref_id is not None
                ),
            )
            metrics_by_ref_id = {m.ref_id: m for m in metrics}

            persons = uow.person_repository.find_all(
                parent_ref_id=person_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.person_ref_id
                    for it in inbox_tasks
                    if it.person_ref_id is not None
                ),
            )
            persons_by_ref_id = {p.ref_id: p for p in persons}

            slack_tasks = uow.slack_task_repository.find_all(
                parent_ref_id=slack_task_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.slack_task_ref_id
                    for it in inbox_tasks
                    if it.slack_task_ref_id is not None
                ),
            )
            slack_tasks_by_ref_id = {p.ref_id: p for p in slack_tasks}

        return InboxTaskFindUseCase.Result(
            inbox_tasks=[
                InboxTaskFindUseCase.ResultEntry(
                    inbox_task=it,
                    project=project_by_ref_id[it.project_ref_id],
                    habit=habits_by_ref_id[it.habit_ref_id]
                    if it.habit_ref_id is not None
                    else None,
                    chore=chores_by_ref_id[it.chore_ref_id]
                    if it.chore_ref_id is not None
                    else None,
                    big_plan=big_plans_by_ref_id[it.big_plan_ref_id]
                    if it.big_plan_ref_id is not None
                    else None,
                    metric=metrics_by_ref_id[it.metric_ref_id]
                    if it.metric_ref_id is not None
                    else None,
                    person=persons_by_ref_id[it.person_ref_id]
                    if it.person_ref_id is not None
                    else None,
                    slack_task=slack_tasks_by_ref_id[it.slack_task_ref_id]
                    if it.slack_task_ref_id is not None
                    else None,
                )
                for it in inbox_tasks
            ]
        )
