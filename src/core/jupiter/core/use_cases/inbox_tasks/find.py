"""The command for finding a inbox task."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.features import Feature, FeatureUnavailableError
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class InboxTaskFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_project_ref_ids: Optional[List[EntityId]] = None
    filter_sources: Optional[List[InboxTaskSource]] = None


@dataclass
class InboxTaskFindResultEntry:
    """A single entry in the load all inbox tasks response."""

    inbox_task: InboxTask
    project: Project
    habit: Optional[Habit] = None
    chore: Optional[Chore] = None
    big_plan: Optional[BigPlan] = None
    metric: Optional[Metric] = None
    person: Optional[Person] = None
    slack_task: Optional[SlackTask] = None
    email_task: Optional[EmailTask] = None


@dataclass
class InboxTaskFindResult(UseCaseResultBase):
    """PersonFindResult."""

    entries: List[InboxTaskFindResultEntry]


class InboxTaskFindUseCase(
    AppLoggedInReadonlyUseCase[InboxTaskFindArgs, InboxTaskFindResult]
):
    """The command for finding a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.INBOX_TASKS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskFindArgs,
    ) -> InboxTaskFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(Feature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(Feature.PROJECTS)

        filter_sources = (
            args.filter_sources
            if args.filter_sources is not None
            else workspace.infer_sources_for_enabled_features(None)
        )

        big_diff = list(
            set(filter_sources).difference(
                workspace.infer_sources_for_enabled_features(filter_sources)
            )
        )
        if len(big_diff) > 0:
            raise FeatureUnavailableError(
                f"Sources {','.join(s.value for s in big_diff)} are not supported in this workspace"
            )

        filter_sources = workspace.infer_sources_for_enabled_features(
            args.filter_sources
        )

        async with self._storage_engine.get_unit_of_work() as uow:
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            habit_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.chore_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            big_plan_collection = (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            push_integrations_group = (
                await uow.push_integration_group_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            slack_task_collection = (
                await uow.slack_task_collection_repository.load_by_parent(
                    push_integrations_group.ref_id,
                )
            )
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integrations_group.ref_id,
                )
            )

            projects = await uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                filter_ref_ids=args.filter_project_ref_ids,
            )
            project_by_ref_id = {p.ref_id: p for p in projects}

            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
                filter_sources=filter_sources,
                filter_project_ref_ids=args.filter_project_ref_ids,
            )

            habits = await uow.habit_repository.find_all(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.habit_ref_id for it in inbox_tasks if it.habit_ref_id is not None
                ),
            )
            habits_by_ref_id = {rt.ref_id: rt for rt in habits}

            chores = await uow.chore_repository.find_all(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.chore_ref_id for it in inbox_tasks if it.chore_ref_id is not None
                ),
            )
            chores_by_ref_id = {rt.ref_id: rt for rt in chores}

            big_plans = await uow.big_plan_repository.find_all(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.big_plan_ref_id
                    for it in inbox_tasks
                    if it.big_plan_ref_id is not None
                ),
            )
            big_plans_by_ref_id = {bp.ref_id: bp for bp in big_plans}

            metrics = await uow.metric_repository.find_all(
                parent_ref_id=metric_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.metric_ref_id
                    for it in inbox_tasks
                    if it.metric_ref_id is not None
                ),
            )
            metrics_by_ref_id = {m.ref_id: m for m in metrics}

            persons = await uow.person_repository.find_all(
                parent_ref_id=person_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.person_ref_id
                    for it in inbox_tasks
                    if it.person_ref_id is not None
                ),
            )
            persons_by_ref_id = {p.ref_id: p for p in persons}

            slack_tasks = await uow.slack_task_repository.find_all(
                parent_ref_id=slack_task_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.slack_task_ref_id
                    for it in inbox_tasks
                    if it.slack_task_ref_id is not None
                ),
            )
            slack_tasks_by_ref_id = {p.ref_id: p for p in slack_tasks}

            email_tasks = await uow.email_task_repository.find_all(
                parent_ref_id=email_task_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=(
                    it.email_task_ref_id
                    for it in inbox_tasks
                    if it.email_task_ref_id is not None
                ),
            )
            email_tasks_by_ref_id = {p.ref_id: p for p in email_tasks}

        return InboxTaskFindResult(
            entries=[
                InboxTaskFindResultEntry(
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
                    email_task=email_tasks_by_ref_id[it.email_task_ref_id]
                    if it.email_task_ref_id is not None
                    else None,
                )
                for it in inbox_tasks
            ],
        )
