"""The command for hard removing a smart list."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.service.remove_service import SmartListRemoveService
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListRemoveUseCase(AppMutationUseCase["SmartListRemoveUseCase.Args", None]):
    """The command for removing a smart list."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        key: SmartListKey

    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )

            smart_list = uow.smart_list_repository.load_by_key(
                smart_list_collection.ref_id, args.key
            )

        smart_list_remove_service = SmartListRemoveService(
            self._storage_engine, self._smart_list_notion_manager
        )
        smart_list_remove_service.execute(smart_list_collection, smart_list)
