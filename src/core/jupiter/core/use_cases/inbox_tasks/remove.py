"""The command for removing a inbox task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
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
class InboxTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class InboxTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskRemoveArgs, None]
):
    """The command for removing a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.INBOX_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(
            args.ref_id,
            allow_archived=True,
        )
        await InboxTaskRemoveService().do_it(uow, progress_reporter, inbox_task)
