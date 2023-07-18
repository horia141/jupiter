"""The command for creating a smart list."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.features import Feature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
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
class SmartListCreateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: SmartListName
    icon: Optional[EntityIcon] = None


@dataclass
class SmartListCreateResult(UseCaseResultBase):
    """SmartListCreate result."""

    new_smart_list: SmartList


class SmartListCreateUseCase(
    AppLoggedInMutationUseCase[SmartListCreateArgs, SmartListCreateResult]
):
    """The command for creating a smart list."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.SMART_LISTS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SmartListCreateArgs,
    ) -> SmartListCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_creating_entity(
            "smart list",
            str(args.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                smart_list_collection = (
                    await uow.smart_list_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )

                new_smart_list = SmartList.new_smart_list(
                    smart_list_collection_ref_id=smart_list_collection.ref_id,
                    name=args.name,
                    icon=args.icon,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                new_smart_list = await uow.smart_list_repository.create(new_smart_list)
                await entity_reporter.mark_known_entity_id(new_smart_list.ref_id)
                await entity_reporter.mark_local_change()

        return SmartListCreateResult(new_smart_list=new_smart_list)
