"""The command for archiving a inbox task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class InboxTaskArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class InboxTaskArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskArchiveArgs, None]
):
    """The command for archiving a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.INBOX_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        inbox_task = await uow.inbox_task_repository.load_by_id(args.ref_id)
        await InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        ).do_it(uow, progress_reporter, inbox_task)
