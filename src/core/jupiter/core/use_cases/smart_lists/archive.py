"""The command for archiving a smart list."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SmartListArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class SmartListArchiveUseCase(AppLoggedInMutationUseCase[SmartListArchiveArgs, None]):
    """The command for archiving a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            smart_list = await uow.smart_list_repository.load_by_id(args.ref_id)

            smart_list_tags = await uow.smart_list_tag_repository.find_all(
                smart_list.ref_id,
            )
            smart_list_items = await uow.smart_list_item_repository.find_all(
                smart_list.ref_id,
            )

        for smart_list_tag in smart_list_tags:
            async with progress_reporter.start_archiving_entity(
                "smart list tag",
                smart_list_tag.ref_id,
                str(smart_list_tag.tag_name),
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    smart_list_tag = smart_list_tag.mark_archived(
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    await uow.smart_list_tag_repository.save(smart_list_tag)
                    await entity_reporter.mark_local_change()

        for smart_list_item in smart_list_items:
            async with progress_reporter.start_archiving_entity(
                "smart list item",
                smart_list_item.ref_id,
                str(smart_list_item.name),
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    smart_list_item = smart_list_item.mark_archived(
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    await uow.smart_list_item_repository.save(smart_list_item)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.start_archiving_entity(
            "smart list",
            smart_list.ref_id,
            str(smart_list.name),
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                smart_list = smart_list.mark_archived(
                    EventSource.CLI,
                    self._time_provider.get_current_time(),
                )
                await uow.smart_list_repository.save(smart_list)
                await entity_reporter.mark_local_change()
