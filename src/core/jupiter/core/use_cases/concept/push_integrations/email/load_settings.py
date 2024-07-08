"""Load settings for email tasks use case."""

from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class EmailTaskLoadSettingsArgs(UseCaseArgsBase):
    """EmailTaskLoadSettings args."""


@use_case_result
class EmailTaskLoadSettingsResult(UseCaseResultBase):
    """EmailTaskLoadSettings results."""

    generation_project: Project


@readonly_use_case(WorkspaceFeature.EMAIL_TASKS, exclude_app=[EventSource.CLI])
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

        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_parent(
            workspace.ref_id,
        )
        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_parent(
            push_integration_group.ref_id,
        )
        generation_project = await uow.get_for(Project).load_by_id(
            email_task_collection.generation_project_ref_id,
        )

        return EmailTaskLoadSettingsResult(generation_project=generation_project)
