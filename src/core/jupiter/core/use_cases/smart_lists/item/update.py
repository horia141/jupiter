"""The command for updating a smart list item."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListItemUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[SmartListItemName]
    is_done: UpdateAction[bool]
    tags: UpdateAction[List[SmartListTagName]]
    url: UpdateAction[Optional[URL]]


class SmartListItemUpdateUseCase(
    AppLoggedInMutationUseCase[SmartListItemUpdateArgs, None]
):
    """The command for updating a smart list item."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListItemUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            smart_list_item = await uow.smart_list_item_repository.load_by_id(
                args.ref_id,
            )

            if args.tags.should_change:
                smart_list_tags = {
                    t.tag_name: t
                    for t in await uow.smart_list_tag_repository.find_all_with_filters(
                        parent_ref_id=smart_list_item.smart_list_ref_id,
                        filter_tag_names=args.tags.just_the_value,
                    )
                }

                for tag in args.tags.just_the_value:
                    if tag in smart_list_tags:
                        continue

                    smart_list_tag = SmartListTag.new_smart_list_tag(
                        smart_list_ref_id=smart_list_item.smart_list_ref_id,
                        tag_name=tag,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    smart_list_tag = await uow.smart_list_tag_repository.create(
                        smart_list_tag,
                    )
                    await progress_reporter.mark_created(smart_list_tag)

                    smart_list_tags[smart_list_tag.tag_name] = smart_list_tag

                tags_ref_id = UpdateAction.change_to(
                    [t.ref_id for t in smart_list_tags.values()],
                )
            else:
                tags_ref_id = UpdateAction.do_nothing()

            smart_list_item = smart_list_item.update(
                name=args.name,
                is_done=args.is_done,
                tags_ref_id=tags_ref_id,
                url=args.url,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            await uow.smart_list_item_repository.save(smart_list_item)
            await progress_reporter.mark_created(smart_list_item)
