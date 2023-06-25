"""The command for creating a smart list tag."""
from dataclasses import dataclass

from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
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
    AppLoggedInMutationUseCase[SmartListTagCreateArgs, SmartListTagCreateResult],
):
    """The command for creating a smart list tag."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListTagCreateArgs,
    ) -> SmartListTagCreateResult:
        """Execute the command's action."""
        async with progress_reporter.start_creating_entity(
            "smart list tag",
            str(args.tag_name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
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
                await entity_reporter.mark_known_entity_id(new_smart_list_tag.ref_id)
                await entity_reporter.mark_local_change()

        return SmartListTagCreateResult(new_smart_list_tag=new_smart_list_tag)
