"""The command for archiving a smart list tag."""
from dataclasses import dataclass

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
class SmartListTagArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListTagArchiveUseCase(
    AppLoggedInMutationUseCase[SmartListTagArchiveArgs, None]
):
    """The command for archiving a smart list tag."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
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
                async with self._storage_engine.get_unit_of_work() as uow:
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

        async with progress_reporter.start_archiving_entity(
            "smart list tag",
            smart_list_tag.ref_id,
        ) as entity_reporter:
            await entity_reporter.mark_known_name(str(smart_list_tag.tag_name))

            async with self._storage_engine.get_unit_of_work() as uow:
                smart_list_tag = smart_list_tag.mark_archived(
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.smart_list_tag_repository.save(smart_list_tag)
                await entity_reporter.mark_local_change()
