"""Update the PRM database."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.change_project_service import InboxTaskChangeProjectService
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PrmDatabaseUpdateCommand(Command['PrmDatabaseUpdateCommand.Args', None]):
    """The command for updating a PRM database."""

    @dataclass()
    class Args:
        """Args."""
        catch_up_project_key: UpdateAction[Optional[ProjectKey]]

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _prm_engine: Final[PrmEngine]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine, project_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            prm_engine: PrmEngine, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._notion_manager = prm_notion_manager
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_engine = prm_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.find()
            old_catch_up_project_ref_id = prm_database.catch_up_project_ref_id

            if args.catch_up_project_key.should_change:
                if args.catch_up_project_key.value is not None:
                    with self._project_engine.get_unit_of_work() as project_uow:
                        project = project_uow.project_repository.get_by_key(args.catch_up_project_key.value)
                    catch_up_project_ref_id = project.ref_id
                else:
                    with self._workspace_engine.get_unit_of_work() as workspace_uow:
                        workspace = workspace_uow.workspace_repository.find()
                    catch_up_project_ref_id = workspace.default_project_ref_id

                prm_database.change_catch_up_project_ref_id(
                    catch_up_project_ref_id, self._time_provider.get_current_time())
            else:
                catch_up_project_ref_id = old_catch_up_project_ref_id

            uow.prm_database_repository.save(prm_database)

            persons = uow.person_repository.find_all(allow_archived=False)

            for person in persons:
                if person.catch_up_params is None:
                    continue
                person.change_catch_up_params(
                    person.catch_up_params.with_new_project_ref_id(
                        catch_up_project_ref_id), self._time_provider.get_current_time())
                uow.person_repository.save(person)

        if old_catch_up_project_ref_id != catch_up_project_ref_id and len(persons) > 0:
            LOGGER.info("Moving all inbox tasks too")
            with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                all_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_person_ref_ids=[p.ref_id for p in persons])
            inbox_task_change_project_service = \
                InboxTaskChangeProjectService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
            for inbox_task in all_inbox_tasks:
                inbox_task_change_project_service.do_it(inbox_task, catch_up_project_ref_id)
