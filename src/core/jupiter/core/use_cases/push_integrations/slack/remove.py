"""The command for hard removing a slack task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SlackTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SlackTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SlackTaskRemoveArgs, None]
):
    """The command for archiving a slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SLACK_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        slack_task = await uow.slack_task_repository.load_by_id(ref_id=args.ref_id)

        slack_task_remove_service = SlackTaskRemoveService()

        await slack_task_remove_service.do_it(uow, progress_reporter, slack_task)
