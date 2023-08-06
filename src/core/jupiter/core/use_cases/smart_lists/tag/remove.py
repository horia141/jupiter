"""The command for removing a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListTagRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListTagRemoveUseCase(
    AppLoggedInMutationUseCase[SmartListTagRemoveArgs, None]
):
    """The command for removing a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            smart_list_tag = await uow.smart_list_tag_repository.load_by_id(args.ref_id)

            smart_list_items = (
                await uow.smart_list_item_repository.find_all_with_filters(
                    parent_ref_id=smart_list_tag.smart_list_ref_id,
                    allow_archived=True,
                    filter_tag_ref_ids=[args.ref_id],
                )
            )

        for smart_list_item in smart_list_items:
            async with progress_reporter.start_updating_entity(
                "smart list item",
                smart_list_item.ref_id,
                str(smart_list_item.name),
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    smart_list_item = smart_list_item.update(
                        name=UpdateAction.do_nothing(),
                        is_done=UpdateAction.do_nothing(),
                        tags_ref_id=UpdateAction.change_to(
                            [
                                t
                                for t in smart_list_item.tags_ref_id
                                if t != args.ref_id
                            ],
                        ),
                        url=UpdateAction.do_nothing(),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await uow.smart_list_item_repository.save(smart_list_item)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.start_removing_entity(
            "smart list tag",
            smart_list_tag.ref_id,
        ) as entity_reporter:
            await entity_reporter.mark_known_name(str(smart_list_tag.tag_name))

            async with self._domain_storage_engine.get_unit_of_work() as uow:
                await uow.smart_list_tag_repository.remove(args.ref_id)
                await entity_reporter.mark_local_change()
