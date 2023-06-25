"""The command for archiving a email task."""
from dataclasses import dataclass

from jupiter.core.domain.push_integrations.email.service.archive_service import (
    EmailTaskArchiveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class EmailTaskArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class EmailTaskArchiveUseCase(AppLoggedInMutationUseCase[EmailTaskArchiveArgs, None]):
    """The command for archiving a email task."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            email_task = await uow.email_task_repository.load_by_id(ref_id=args.ref_id)

        email_task_archive_service = EmailTaskArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._storage_engine,
        )

        await email_task_archive_service.do_it(progress_reporter, email_task)
