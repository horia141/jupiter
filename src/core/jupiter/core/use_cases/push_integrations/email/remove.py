"""The command for hard removing a email task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
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
class EmailTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class EmailTaskRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[EmailTaskRemoveArgs, None]
):
    """The command for archiving a email task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.EMAIL_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        email_task = await uow.email_task_repository.load_by_id(ref_id=args.ref_id)

        email_task_remove_service = EmailTaskRemoveService()

        await email_task_remove_service.do_it(uow, progress_reporter, email_task)
