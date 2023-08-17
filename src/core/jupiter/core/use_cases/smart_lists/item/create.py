"""The command for creating a smart list item."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.url import URL
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
class SmartListItemCreateArgs(UseCaseArgsBase):
    """SmartListItemCreate args."""

    smart_list_ref_id: EntityId
    name: SmartListItemName
    is_done: bool
    tag_names: List[SmartListTagName]
    url: Optional[URL] = None


@dataclass
class SmartListItemCreateResult(UseCaseResultBase):
    """SmartListItemCreate result."""

    new_smart_list_item: SmartListItem


class SmartListItemCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        SmartListItemCreateArgs, SmartListItemCreateResult
    ],
):
    """The command for creating a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SMART_LISTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemCreateArgs,
    ) -> SmartListItemCreateResult:
        """Execute the command's action."""
        smart_list = await uow.smart_list_repository.load_by_id(
            args.smart_list_ref_id,
        )
        smart_list_tags = {
            t.tag_name: t
            for t in await uow.smart_list_tag_repository.find_all_with_filters(
                parent_ref_id=smart_list.ref_id,
                filter_tag_names=args.tag_names,
            )
        }

        for tag_name in args.tag_names:
            if tag_name in smart_list_tags:
                continue

            smart_list_tag = SmartListTag.new_smart_list_tag(
                smart_list_ref_id=smart_list.ref_id,
                tag_name=tag_name,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time(),
            )
            smart_list_tag = await uow.smart_list_tag_repository.create(
                smart_list_tag,
            )
            await progress_reporter.mark_created(smart_list_tag)
            smart_list_tags[smart_list_tag.tag_name] = smart_list_tag

        new_smart_list_item = SmartListItem.new_smart_list_item(
            archived=False,
            smart_list_ref_id=smart_list.ref_id,
            name=args.name,
            is_done=args.is_done,
            tags_ref_id=[t.ref_id for t in smart_list_tags.values()],
            url=args.url,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_smart_list_item = await uow.smart_list_item_repository.create(
            new_smart_list_item,
        )
        await progress_reporter.mark_created(new_smart_list_item)

        return SmartListItemCreateResult(new_smart_list_item=new_smart_list_item)
