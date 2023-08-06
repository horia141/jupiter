"""The command for removing a inbox task."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
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
class InboxTaskRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class InboxTaskRemoveUseCase(AppLoggedInMutationUseCase[InboxTaskRemoveArgs, None]):
    """The command for removing a inbox task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.INBOX_TASKS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: InboxTaskRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            inbox_task = await uow.inbox_task_repository.load_by_id(
                args.ref_id,
                allow_archived=True,
            )
        await InboxTaskRemoveService(
            self._domain_storage_engine,
        ).do_it(progress_reporter, inbox_task)
