"""Load settings for email tasks use case."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
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
class SlackTaskLoadSettingsArgs(UseCaseArgsBase):
    """SlackTaskLoadSettings args."""


@use_case_result
class SlackTaskLoadSettingsResult(UseCaseResultBase):
    """SlackTaskLoadSettings results."""

    generation_project: Project


@readonly_use_case(WorkspaceFeature.SLACK_TASKS, exclude_app=[EventSource.CLI])
class SlackTaskLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        SlackTaskLoadSettingsArgs, SlackTaskLoadSettingsResult
    ],
):
    """The command for loading the settings around slack tasks."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: SlackTaskLoadSettingsArgs,
    ) -> SlackTaskLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

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
        generation_project = await uow.get_for(Project).load_by_id(
            slack_task_collection.generation_project_ref_id,
        )

        return SlackTaskLoadSettingsResult(generation_project=generation_project)
