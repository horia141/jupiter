"""The command for creating a smart list item."""
from typing import List, Optional

from jupiter.core.domain.core.url import URL
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class SmartListItemCreateArgs(UseCaseArgsBase):
    """SmartListItemCreate args."""

    smart_list_ref_id: EntityId
    name: SmartListItemName
    is_done: bool
    tag_names: List[SmartListTagName]
    url: Optional[URL] = None


@use_case_result
class SmartListItemCreateResult(UseCaseResultBase):
    """SmartListItemCreate result."""

    new_smart_list_item: SmartListItem


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListItemCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        SmartListItemCreateArgs, SmartListItemCreateResult
    ],
):
    """The command for creating a smart list item."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListItemCreateArgs,
    ) -> SmartListItemCreateResult:
        """Execute the command's action."""
        smart_list, tags = await generic_loader(
            uow, SmartList, args.smart_list_ref_id, SmartList.tags
        )
        smart_list_tags = {t.tag_name: t for t in tags if t.tag_name in args.tag_names}

        for tag_name in args.tag_names:
            if tag_name in smart_list_tags:
                continue

            smart_list_tag = SmartListTag.new_smart_list_tag(
                ctx=context.domain_context,
                smart_list_ref_id=smart_list.ref_id,
                tag_name=tag_name,
            )
            smart_list_tag = await uow.smart_list_tag_repository.create(
                smart_list_tag,
            )
            await progress_reporter.mark_created(smart_list_tag)
            smart_list_tags[smart_list_tag.tag_name] = smart_list_tag

        new_smart_list_item = SmartListItem.new_smart_list_item(
            ctx=context.domain_context,
            smart_list_ref_id=smart_list.ref_id,
            name=args.name,
            is_done=args.is_done,
            tags_ref_id=[t.ref_id for t in smart_list_tags.values()],
            url=args.url,
        )
        new_smart_list_item = await uow.smart_list_item_repository.create(
            new_smart_list_item,
        )
        await progress_reporter.mark_created(new_smart_list_item)

        return SmartListItemCreateResult(new_smart_list_item=new_smart_list_item)
