"""The command for updating a smart list tag."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
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
class SmartListTagUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    tag_name: UpdateAction[SmartListTagName]


class SmartListTagUpdateUseCase(
    AppLoggedInMutationUseCase[SmartListTagUpdateArgs, None]
):
    """The command for updating a smart list tag."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "smart list tag",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                smart_list_tag = await uow.smart_list_tag_repository.load_by_id(
                    args.ref_id
                )
                await entity_reporter.mark_known_name(str(smart_list_tag.tag_name))
                smart_list_tag = smart_list_tag.update(
                    tag_name=args.tag_name,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await entity_reporter.mark_known_name(str(smart_list_tag.tag_name))

                await uow.smart_list_tag_repository.save(smart_list_tag)
                await entity_reporter.mark_local_change()
