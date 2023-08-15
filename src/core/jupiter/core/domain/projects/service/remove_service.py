"""Shared logic for removing a project."""
from typing import Final

from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class ProjectRemoveService:
    """Shared logic for removing a project."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        ref_id: EntityId,
    ) -> None:
        """Remove the project."""
        project = await uow.project_repository.load_by_id(ref_id, allow_archived=True)

        # test it's not the workspace default project nor a metric collection project nor a person catchup one
        if workspace.default_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the workspace default one"
            )
        metric_collection = await uow.metric_collection_repository.load_by_parent(
            workspace.ref_id
        )
        if metric_collection.collection_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the metric collection default one"
            )
        person_collection = await uow.person_collection_repository.load_by_parent(
            workspace.ref_id
        )
        if person_collection.catch_up_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the person catch up one"
            )
        push_integration_group = (
            await uow.push_integration_group_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        slack_task_collection = (
            await uow.slack_task_collection_repository.load_by_parent(
                push_integration_group.ref_id,
            )
        )
        if slack_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the Slack task collection default one"
            )
        email_task_collection = (
            await uow.email_task_collection_repository.load_by_parent(
                push_integration_group.ref_id,
            )
        )
        if email_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the email task collection default one"
            )

        # remove inbox tasks
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(workspace.ref_id)
        )
        inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_project_ref_ids=[project.ref_id],
        )
        inbox_task_remove_service = InboxTaskRemoveService()
        for it in inbox_tasks:
            await inbox_task_remove_service.do_it(uow, progress_reporter, it)

        # remove chores
        chore_collection = await uow.chore_collection_repository.load_by_parent(
            workspace.ref_id
        )
        chores = await uow.chore_repository.find_all_with_filters(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            filter_project_ref_ids=[project.ref_id],
        )
        chore_remove_service = ChoreRemoveService()
        for chore in chores:
            await chore_remove_service.remove(uow, progress_reporter, chore.ref_id)

        # remove habits
        habit_collection = await uow.habit_collection_repository.load_by_parent(
            workspace.ref_id
        )
        habits = await uow.habit_repository.find_all_with_filters(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            filter_project_ref_ids=[project.ref_id],
        )
        habit_remove_service = HabitRemoveService()
        for habit in habits:
            await habit_remove_service.remove(uow, progress_reporter, habit.ref_id)

        # remove big plans
        big_plan_collection = await uow.habit_collection_repository.load_by_parent(
            workspace.ref_id
        )
        big_plans = await uow.big_plan_repository.find_all_with_filters(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            filter_project_ref_ids=[project.ref_id],
        )
        big_plan_remove_service = BigPlanRemoveService()
        for big_plan in big_plans:
            await big_plan_remove_service.remove(
                uow, progress_reporter, workspace, big_plan.ref_id
            )

        # remove project
        await uow.project_repository.remove(project.ref_id)
        await progress_reporter.mark_removed(project)
