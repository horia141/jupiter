"""The command for hard removing a email task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class EmailTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class EmailTaskRemoveUseCase(AppLoggedInMutationUseCase[EmailTaskRemoveArgs, None]):
    """The command for archiving a email task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.EMAIL_TASKS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            email_task = await uow.email_task_repository.load_by_id(ref_id=args.ref_id)

        email_task_remove_service = EmailTaskRemoveService(
            self._storage_engine,
        )

        await email_task_remove_service.do_it(progress_reporter, email_task)
