"""The command for updating a smart list item."""

from jupiter.core.domain.concept.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.concept.smart_lists.smart_list_item_name import (
    SmartListItemName,
)
from jupiter.core.domain.concept.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.domain.core.url import URL
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class SmartListItemUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[SmartListItemName]
    is_done: UpdateAction[bool]
    tags: UpdateAction[list[TagName]]
    url: UpdateAction[URL | None]


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListItemUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListItemUpdateArgs, None]
):
    """The command for updating a smart list item."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListItemUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_item, all_tags = await generic_loader(
            uow, SmartListItem, args.ref_id, SmartListItem.all_tags
        )

        if args.tags.should_change:
            smart_list_tags = {}
            all_smart_list_tags = {t.tag_name.the_tag: t.ref_id for t in all_tags}

            for tag in args.tags.just_the_value:
                if tag.the_tag in all_smart_list_tags:
                    smart_list_tags[tag.the_tag] = all_smart_list_tags[tag.the_tag]
                    continue

                smart_list_tag = SmartListTag.new_smart_list_tag(
                    ctx=context.domain_context,
                    smart_list_ref_id=smart_list_item.smart_list.ref_id,
                    tag_name=tag,
                )
                smart_list_tag = await generic_creator(
                    uow, progress_reporter, smart_list_tag
                )
                smart_list_tags[smart_list_tag.tag_name.the_tag] = smart_list_tag.ref_id
                all_smart_list_tags[
                    smart_list_tag.tag_name.the_tag
                ] = smart_list_tag.ref_id

            tags_ref_id = UpdateAction.change_to(
                list(smart_list_tags.values()),
            )
        else:
            tags_ref_id = UpdateAction.do_nothing()

        smart_list_item = smart_list_item.update(
            ctx=context.domain_context,
            name=args.name,
            is_done=args.is_done,
            tags_ref_id=tags_ref_id,
            url=args.url,
        )

        await uow.get_for(SmartListItem).save(smart_list_item)
        await progress_reporter.mark_updated(smart_list_item)
