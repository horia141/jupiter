"""Shared logic for archiving a project."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.chores.service.archive_service import ChoreArchiveService
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.service.archive_service import HabitArchiveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task_collection import EmailTaskCollection
from jupiter.core.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.core.domain.push_integrations.slack.slack_task_collection import SlackTaskCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class ProjectArchiveService:
    """Shared logic for archiving a project."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        ref_id: EntityId,
    ) -> None:
        """Archive the project."""
        project = await uow.repository_for(Project).load_by_id(ref_id, allow_archived=False)

        # test it's not the workspace default project nor a metric collection project nor a person catchup one
        if workspace.default_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the workspace default one"
            )
        metric_collection = await uow.repository_for(MetricCollection).load_by_parent(
            workspace.ref_id
        )
        if metric_collection.collection_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the metric collection default one"
            )
        person_collection = await uow.repository_for(PersonCollection).load_by_parent(
            workspace.ref_id
        )
        if person_collection.catch_up_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the person catch up one"
            )

        push_integration_group = (
            await uow.repository_for(PushIntegrationGroup).load_by_parent(
                workspace.ref_id,
            )
        )
        slack_task_collection = (
            await uow.repository_for(SlackTaskCollection).load_by_parent(
                push_integration_group.ref_id,
            )
        )
        if slack_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the Slack task collection default one"
            )
        email_task_collection = (
            await uow.repository_for(EmailTaskCollection).load_by_parent(
                push_integration_group.ref_id,
            )
        )
        if email_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the email task collection default one"
            )

        # archive inbox tasks
        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(workspace.ref_id)
        )
        inbox_tasks = await uow.repository_for(InboxTask).find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_project_ref_ids=[project.ref_id],
        )
        inbox_task_archive_service = InboxTaskArchiveService()
        for it in inbox_tasks:
            await inbox_task_archive_service.do_it(ctx, uow, progress_reporter, it)

        # archive chores
        chore_collection = await uow.repository_for(ChoreCollection).load_by_parent(
            workspace.ref_id
        )
        chores = await uow.repository_for(Chore).find_all_with_filters(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=False,
            filter_project_ref_ids=[project.ref_id],
        )
        chore_archive_service = ChoreArchiveService()
        for chore in chores:
            await chore_archive_service.do_it(ctx, uow, progress_reporter, chore)

        # archive habits
        habit_collection = await uow.repository_for(HabitCollection).load_by_parent(
            workspace.ref_id
        )
        habits = await uow.repository_for(Habit).find_all_with_filters(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=False,
            filter_project_ref_ids=[project.ref_id],
        )
        habit_archive_service = HabitArchiveService()
        for habit in habits:
            await habit_archive_service.do_it(ctx, uow, progress_reporter, habit)

        # archive big plans
        big_plan_collection = await uow.repository_for(HabitCollection).load_by_parent(
            workspace.ref_id
        )
        big_plans = await uow.repository_for(BigPlan).find_all_with_filters(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=False,
            filter_project_ref_ids=[project.ref_id],
        )
        big_plan_archive_service = BigPlanArchiveService()
        for big_plan in big_plans:
            await big_plan_archive_service.do_it(ctx, uow, progress_reporter, big_plan)

        # archive project
        project = project.mark_archived(ctx)
        await uow.repository_for(Project).save(project)
        await progress_reporter.mark_updated(project)
