"""Use case for archiving a project."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.service.archive_service import ProjectArchiveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class ProjectArchiveArgs(UseCaseArgsBase):
    """Project archive args."""

    ref_id: EntityId
    backup_project_ref_id: Optional[EntityId] = None


@mutation_use_case(WorkspaceFeature.PROJECTS)
class ProjectArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectArchiveArgs, None]
):
    """The command for archiving a project."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ProjectArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        if args.backup_project_ref_id:
            if context.workspace.default_project_ref_id == args.ref_id:
                workspace = workspace.change_default_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.workspace_repository.save(workspace)

            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            if metric_collection.collection_project_ref_id == args.ref_id:
                metric_collection = metric_collection.change_collection_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.metric_collection_repository.save(metric_collection)

            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id
            )
            if person_collection.catch_up_project_ref_id == args.ref_id:
                person_collection = person_collection.change_catch_up_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.person_collection_repository.save(person_collection)

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
            if slack_task_collection.generation_project_ref_id == args.ref_id:
                slack_task_collection = slack_task_collection.change_generation_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.slack_task_collection_repository.save(slack_task_collection)

            push_integration_group = (
                await uow.push_integration_group_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )
            if email_task_collection.generation_project_ref_id == args.ref_id:
                email_task_collection = email_task_collection.change_generation_project(
                    context.domain_context,
                    args.backup_project_ref_id,
                )
                await uow.email_task_collection_repository.save(email_task_collection)

        project_archive_service = ProjectArchiveService()
        await project_archive_service.do_it(
            context.domain_context, uow, progress_reporter, workspace, args.ref_id
        )
