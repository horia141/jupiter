"""Update the PRM database."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.change_project_service import InboxTaskChangeProjectService
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PrmDatabaseChangeCatchUpProjectUseCase(UseCase['PrmDatabaseChangeCatchUpProjectUseCase.Args', None]):
    """The command for updating a PRM database."""

    @dataclass()
    class Args:
        """Args."""
        catch_up_project_key: Optional[ProjectKey]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = workspace_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            old_catch_up_project_ref_id = prm_database.catch_up_project_ref_id

            if args.catch_up_project_key is not None:
                project = uow.project_repository.load_by_key(args.catch_up_project_key)
                catch_up_project_ref_id = project.ref_id
            else:
                workspace = uow.workspace_repository.load()
                catch_up_project_ref_id = workspace.default_project_ref_id

            prm_database.change_catch_up_project(
                catch_up_project_ref_id=catch_up_project_ref_id, source=EventSource.CLI,
                modified_time=self._time_provider.get_current_time())

            uow.prm_database_repository.save(prm_database)

            persons = uow.person_repository.find_all(allow_archived=False)

            for person in persons:
                if person.catch_up_params is None:
                    continue
                person.change_catch_up_project(
                    catch_up_project_ref_id=catch_up_project_ref_id, source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())
                uow.person_repository.save(person)

        if old_catch_up_project_ref_id != catch_up_project_ref_id and len(persons) > 0:
            LOGGER.info("Moving all inbox tasks too")
            with self._storage_engine.get_unit_of_work() as inbox_task_uow:
                all_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_person_ref_ids=[p.ref_id for p in persons])
            inbox_task_change_project_service = \
                InboxTaskChangeProjectService(
                    source=EventSource.CLI, time_provider=self._time_provider, storage_engine=self._storage_engine,
                    inbox_task_notion_manager=self._inbox_task_notion_manager)
            for inbox_task in all_inbox_tasks:
                inbox_task_change_project_service.do_it(inbox_task, catch_up_project_ref_id)
