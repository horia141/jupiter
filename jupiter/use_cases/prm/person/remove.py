"""Remove a person."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.prm.service.remove_service import PersonRemoveService
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a person."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            person = uow.person_repository.load_by_id(args)

        PersonRemoveService(self._storage_engine, self._prm_notion_manager, self._inbox_task_notion_manager)\
            .do_it(person)
