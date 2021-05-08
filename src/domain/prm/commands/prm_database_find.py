"""The command for finding the PRM database."""
from dataclasses import dataclass
from typing import List, Optional, Final

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.person import Person
from domain.prm.prm_database import PrmDatabase
from models.basic import EntityId
from models.framework import Command
from service.inbox_tasks import InboxTasksService
from service.projects import Project, ProjectsService


class PrmDatabaseFindCommand(Command['PrmDatabaseFindCommand.Args', 'PrmDatabaseFindCommand.Response']):
    """The command for finding the PRM Database."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_person_ref_ids: Optional[List[EntityId]]


    @dataclass()
    class Response:
        """Response."""

        prm_database: PrmDatabase
        catch_up_project: Project
        persons: List[Person]

    _engine: Final[PrmEngine]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, engine: PrmEngine, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._engine = engine
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: Args) -> 'PrmDatabaseFindCommand.Response':
        """Execute the command's action."""
        with self._engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            catch_up_project = self._projects_service.load_project_by_ref_id(prm_database.catch_up_project_ref_id)
            persons = uow.person_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_person_ref_ids)

        return self.Response(
            prm_database=prm_database,
            catch_up_project=catch_up_project,
            persons=persons)
