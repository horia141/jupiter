"""The command for creating a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SmartListTagCreateArgs(UseCaseArgsBase):
    """SmartListTagCreate args."""

    smart_list_ref_id: EntityId
    tag_name: SmartListTagName


@dataclass
class SmartListTagCreateResult(UseCaseResultBase):
    """SmartListTagCreate result."""

    new_smart_list_tag: SmartListTag


class SmartListTagCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        SmartListTagCreateArgs, SmartListTagCreateResult
    ],
):
    """The command for creating a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagCreateArgs,
    ) -> SmartListTagCreateResult:
        """Execute the command's action."""
        metric = await uow.smart_list_repository.load_by_id(
            args.smart_list_ref_id,
        )
        new_smart_list_tag = SmartListTag.new_smart_list_tag(
            smart_list_ref_id=metric.ref_id,
            tag_name=args.tag_name,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_smart_list_tag = await uow.smart_list_tag_repository.create(
            new_smart_list_tag,
        )
        await progress_reporter.mark_created(new_smart_list_tag)

        return SmartListTagCreateResult(new_smart_list_tag=new_smart_list_tag)
