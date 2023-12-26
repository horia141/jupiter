"""Load settings for email tasks use case."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@dataclass
class EmailTaskLoadSettingsArgs(UseCaseArgsBase):
    """EmailTaskLoadSettings args."""


@dataclass
class EmailTaskLoadSettingsResult(UseCaseResultBase):
    """EmailTaskLoadSettings results."""

    generation_project: Project


@readonly_use_case(WorkspaceFeature.EMAIL_TASKS)
class EmailTaskLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        EmailTaskLoadSettingsArgs, EmailTaskLoadSettingsResult
    ],
):
    """The command for loading the settings around email tasks."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: EmailTaskLoadSettingsArgs,
    ) -> EmailTaskLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

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
        generation_project = await uow.project_repository.load_by_id(
            email_task_collection.generation_project_ref_id,
        )

        return EmailTaskLoadSettingsResult(generation_project=generation_project)
