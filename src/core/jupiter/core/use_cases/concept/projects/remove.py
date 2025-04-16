"""Use case for removing a project."""

from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.concept.projects.service.check_cycles_service import (
    ProjectCheckCyclesService,
    ProjectTreeHasCyclesError,
)
from jupiter.core.domain.concept.projects.service.remove_service import (
    ProjectRemoveService,
)
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.concept.working_mem.working_mem_collection import (
    WorkingMemCollection,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ProjectRemoveArgs(UseCaseArgsBase):
    """Project remove args."""

    ref_id: EntityId
    backup_project_ref_id: EntityId | None


@mutation_use_case(WorkspaceFeature.PROJECTS)
class ProjectRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectRemoveArgs, None]
):
    """The command for removing a project."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ProjectRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        project = await uow.get_for(Project).load_by_id(args.ref_id)

        if project.is_root:
            raise InputValidationError("The root project cannot be archived")

        if args.backup_project_ref_id:
            time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
                workspace.ref_id
            )
            if time_plan_domain.planning_task_project_ref_id == args.ref_id:
                time_plan_domain = time_plan_domain.change_planning_task_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(TimePlanDomain).save(time_plan_domain)

            journal_collection = await uow.get_for(JournalCollection).load_by_parent(
                workspace.ref_id
            )
            if journal_collection.writing_task_project_ref_id == args.ref_id:
                journal_collection = journal_collection.change_writing_task_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(JournalCollection).save(journal_collection)

            metric_collection = await uow.get_for(MetricCollection).load_by_parent(
                workspace.ref_id
            )
            if metric_collection.collection_project_ref_id == args.ref_id:
                metric_collection = metric_collection.change_collection_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(MetricCollection).save(metric_collection)

            person_collection = await uow.get_for(PersonCollection).load_by_parent(
                workspace.ref_id
            )
            if person_collection.catch_up_project_ref_id == args.ref_id:
                person_collection = person_collection.change_catch_up_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(PersonCollection).save(person_collection)

            push_integration_group = await uow.get_for(
                PushIntegrationGroup
            ).load_by_parent(
                workspace.ref_id,
            )
            slack_task_collection = await uow.get_for(
                SlackTaskCollection
            ).load_by_parent(
                push_integration_group.ref_id,
            )
            if slack_task_collection.generation_project_ref_id == args.ref_id:
                slack_task_collection = slack_task_collection.change_generation_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(SlackTaskCollection).save(slack_task_collection)

            push_integration_group = await uow.get_for(
                PushIntegrationGroup
            ).load_by_parent(
                workspace.ref_id,
            )
            email_task_collection = await uow.get_for(
                EmailTaskCollection
            ).load_by_parent(
                push_integration_group.ref_id,
            )
            if email_task_collection.generation_project_ref_id == args.ref_id:
                email_task_collection = email_task_collection.change_generation_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(EmailTaskCollection).save(email_task_collection)

            working_mem_collection = await uow.get_for(
                WorkingMemCollection
            ).load_by_parent(workspace.ref_id)
            if working_mem_collection.cleanup_project_ref_id == args.ref_id:
                working_mem_collection = working_mem_collection.change_cleanup_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.get_for(WorkingMemCollection).save(working_mem_collection)

            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id
            )
            child_projects = await uow.get_for(Project).find_all_generic(
                parent_ref_id=project_collection.ref_id,
                allow_archived=True,
                parent_project_ref_id=args.ref_id,
            )
            for child_project in child_projects:
                child_project = child_project.change_parent(
                    context.domain_context, args.backup_project_ref_id
                )

                await uow.get_for(Project).save(child_project)
                await progress_reporter.mark_updated(child_project)

                try:
                    await ProjectCheckCyclesService().check_for_cycles(
                        uow, child_project
                    )
                except ProjectTreeHasCyclesError as err:
                    raise InputValidationError("The project tree has cycles.") from err

        project_remove_service = ProjectRemoveService()
        await project_remove_service.do_it(
            context.domain_context, uow, progress_reporter, context.workspace, project
        )
