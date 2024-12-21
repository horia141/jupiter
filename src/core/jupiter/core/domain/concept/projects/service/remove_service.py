"""Shared logic for removing a project."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.service.remove_service import (
    BigPlanRemoveService,
)
from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_collection import ChoreCollection
from jupiter.core.domain.concept.chores.service.remove_service import ChoreRemoveService
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_collection import HabitCollection
from jupiter.core.domain.concept.habits.service.remove_service import HabitRemoveService
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class ProjectRemoveService:
    """Shared logic for removing a project."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        project: Project,
    ) -> None:
        """Remove the project."""
        if project.is_root:
            raise Exception("The root project cannot be removed")

        # test it's not the workspace default project nor a metric collection project nor a person catchup one
        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id
        )
        if metric_collection.collection_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the metric collection default one"
            )
        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id
        )
        if person_collection.catch_up_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the person catch up one"
            )
        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_parent(
            workspace.ref_id,
        )
        slack_task_collection = await uow.get_for(SlackTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )
        if slack_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the Slack task collection default one"
            )
        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )
        if email_task_collection.generation_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the email task collection default one"
            )
        working_mem_collection = await uow.get_for(WorkingMemCollection).load_by_parent(
            workspace.ref_id
        )
        if working_mem_collection.cleanup_project_ref_id == project.ref_id:
            raise ProjectInSignificantUseError(
                "The project is being used as the working memory cleanup tasks default one"
            )

        # remove inbox tasks
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id
        )
        inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            project_ref_id=[project.ref_id],
        )
        inbox_task_remove_service = InboxTaskRemoveService()
        for it in inbox_tasks:
            await inbox_task_remove_service.do_it(ctx, uow, progress_reporter, it)

        # remove chores
        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
            workspace.ref_id
        )
        chores = await uow.get_for(Chore).find_all_generic(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=True,
            projedct_ref_id=[project.ref_id],
        )
        chore_remove_service = ChoreRemoveService()
        for chore in chores:
            await chore_remove_service.remove(ctx, uow, progress_reporter, chore.ref_id)

        # remove habits
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id
        )
        habits = await uow.get_for(Habit).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=True,
            project_ref_id=[project.ref_id],
        )
        habit_remove_service = HabitRemoveService()
        for habit in habits:
            await habit_remove_service.remove(ctx, uow, progress_reporter, habit.ref_id)

        # remove big plans
        big_plan_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id
        )
        big_plans = await uow.get_for(BigPlan).find_all_generic(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=True,
            project_ref_id=[project.ref_id],
        )
        big_plan_remove_service = BigPlanRemoveService()
        for big_plan in big_plans:
            await big_plan_remove_service.remove(
                ctx, uow, progress_reporter, workspace, big_plan.ref_id
            )

        # remove note
        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            ctx, uow, NoteDomain.PROJECT, project.ref_id
        )

        # remove child projects
        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id
        )
        child_projects = await uow.get_for(Project).find_all_generic(
            parent_ref_id=project_collection.ref_id,
            allow_archived=True,
            parent_project_ref_id=project.ref_id,
        )
        for child_project in child_projects:
            await self.do_it(ctx, uow, progress_reporter, workspace, child_project)

        # remove from parent project list
        parent_project = await uow.get_for(Project).load_by_id(
            project.surely_parent_project_ref_id
        )
        parent_project = parent_project.remove_child_project(ctx, project.ref_id)
        await uow.get_for(Project).save(parent_project)

        # remove project
        await uow.get_for(Project).remove(project.ref_id)
        await progress_reporter.mark_removed(project)
