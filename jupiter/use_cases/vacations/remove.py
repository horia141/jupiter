"""The command for removing a vacation entry."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class VacationRemoveUseCase(AppMutationUseCase['VacationRemoveUseCase.Args', None]):
    """The command for removing a vacation."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            vacation_notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._vacation_notion_manager = vacation_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_parent(workspace.ref_id)
            uow.vacation_repository.remove(args.ref_id)

        try:
            self._vacation_notion_manager.remove_leaf(vacation_collection.ref_id, args.ref_id)
        except NotionVacationNotFoundError:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")
