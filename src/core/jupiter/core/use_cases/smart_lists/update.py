"""The command for updating a smart list."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SmartListUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[SmartListName]
    icon: UpdateAction[Optional[EntityIcon]]


class SmartListUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListUpdateArgs, None]
):
    """The command for updating a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.smart_list_repository.load_by_id(
            args.ref_id,
        )

        smart_list = smart_list.update(
            name=args.name,
            icon=args.icon,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.smart_list_repository.save(smart_list)
        await progress_reporter.mark_updated(smart_list)
