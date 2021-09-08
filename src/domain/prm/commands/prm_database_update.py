"""Update the PRM database."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, cast, Dict

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person import Person
from domain.common.recurring_task_gen_params import RecurringTaskGenParams
from domain.common.timestamp import Timestamp
from domain.projects.project_key import ProjectKey
from models.framework import Command, UpdateAction, EntityId
from service.errors import ServiceError
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.workspaces import WorkspacesService
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class PrmDatabaseUpdateCommand(Command['PrmDatabaseUpdateCommand.Args', None]):
    """The command for updating a PRM database."""

    @dataclass()
    class Args:
        """Args."""
        catch_up_project_key: UpdateAction[Optional[ProjectKey]]

    _time_provider: Final[TimeProvider]
    _engine: Final[PrmEngine]
    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, time_provider: TimeProvider, engine: PrmEngine,
            notion_manager: PrmNotionManager, workspaces_service: WorkspacesService,
            projects_service: ProjectsService, inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._engine = engine
        self._notion_manager = notion_manager
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            old_catch_up_project_ref_id = prm_database.catch_up_project_ref_id

            if args.catch_up_project_key.should_change:
                if args.catch_up_project_key.value is not None:
                    project = self._projects_service.load_project_by_key(args.catch_up_project_key.value)
                    catch_up_project_ref_id = project.ref_id
                else:
                    workspace = self._workspaces_service.load_workspace()
                    if workspace.default_project_ref_id is None:
                        raise ServiceError("Cannot speficy an empty catch up project without a default workspace one")
                    catch_up_project_ref_id = workspace.default_project_ref_id

                prm_database.change_catch_up_project_ref_id(
                    catch_up_project_ref_id, self._time_provider.get_current_time())
            else:
                catch_up_project_ref_id = old_catch_up_project_ref_id

            uow.prm_database_repository.save(prm_database)

            persons = uow.person_repository.find_all(allow_archived=False)
            persons_by_ref_id: Dict[EntityId, Person] = {p.ref_id: p for p in persons}

            for person in persons:
                if person.catch_up_params is None:
                    continue
                person.change_catch_up_params(
                    person.catch_up_params.with_new_project_ref_id(
                        catch_up_project_ref_id), self._time_provider.get_current_time())
                uow.person_repository.save(person)

        if old_catch_up_project_ref_id != catch_up_project_ref_id and len(persons) > 0:
            LOGGER.info("Moving all inbox tasks too")
            for inbox_task in self._inbox_tasks_service.load_all_inbox_tasks(
                    allow_archived=True, filter_person_ref_ids=[p.ref_id for p in persons]):
                owner_person = persons_by_ref_id[cast(EntityId, inbox_task.person_ref_id)]
                self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
                self._inbox_tasks_service.create_inbox_task_for_person(
                    project_ref_id=catch_up_project_ref_id,
                    name=inbox_task.name,
                    person_ref_id=cast(EntityId, inbox_task.person_ref_id),
                    recurring_task_timeline=cast(str, inbox_task.recurring_timeline),
                    recurring_task_period=cast(RecurringTaskGenParams, owner_person.catch_up_params).period,
                    recurring_task_gen_right_now=cast(Timestamp, inbox_task.recurring_gen_right_now),
                    eisen=inbox_task.eisen,
                    difficulty=inbox_task.difficulty,
                    actionable_date=inbox_task.actionable_date,
                    due_date=inbox_task.due_date)
