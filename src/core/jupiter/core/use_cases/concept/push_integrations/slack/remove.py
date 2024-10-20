"""The command for hard removing a slack task."""

from jupiter.core.domain.concept.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class SlackTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SLACK_TASKS)
class SlackTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SlackTaskRemoveArgs, None]
):
    """The command for archiving a slack task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SlackTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        slack_task = await uow.get_for(SlackTask).load_by_id(ref_id=args.ref_id)

        slack_task_remove_service = SlackTaskRemoveService()

        await slack_task_remove_service.do_it(
            context.domain_context, uow, progress_reporter, slack_task
        )
