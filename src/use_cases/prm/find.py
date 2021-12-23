"""The command for finding the PRM database."""
from dataclasses import dataclass
from typing import List, Optional, Final

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.person import Person
from domain.prm.prm_database import PrmDatabase
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project import Project
from framework.entity_id import EntityId
from framework.use_case import UseCase


class PrmDatabaseFindUseCase(UseCase['PrmDatabaseFindUseCase.Args', 'PrmDatabaseFindUseCase.Response']):
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

    _prm_engine: Final[PrmEngine]
    _project_engine: Final[ProjectEngine]

    def __init__(
            self, prm_engine: PrmEngine, project_engine: ProjectEngine) -> None:
        """Constructor."""
        self._prm_engine = prm_engine
        self._project_engine = project_engine

    def execute(self, args: Args) -> 'PrmDatabaseFindUseCase.Response':
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as prm_uow:
            with self._project_engine.get_unit_of_work() as project_uow:
                prm_database = prm_uow.prm_database_repository.load()
                catch_up_project = project_uow.project_repository.load_by_id(prm_database.catch_up_project_ref_id)
                persons = prm_uow.person_repository.find_all(
                    allow_archived=args.allow_archived, filter_ref_ids=args.filter_person_ref_ids)

        return self.Response(
            prm_database=prm_database,
            catch_up_project=catch_up_project,
            persons=persons)
