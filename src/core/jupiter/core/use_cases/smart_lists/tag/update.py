"""The command for updating a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
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
class SmartListTagUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    tag_name: UpdateAction[SmartListTagName]


class SmartListTagUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListTagUpdateArgs, None]
):
    """The command for updating a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_tag = await uow.smart_list_tag_repository.load_by_id(args.ref_id)
        smart_list_tag = smart_list_tag.update(
            tag_name=args.tag_name,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.smart_list_tag_repository.save(smart_list_tag)
        await progress_reporter.mark_updated(smart_list_tag)
