"""The command for finding the PRM database."""
from dataclasses import dataclass
from typing import List, Optional, Final

from jupiter.domain.prm.person import Person
from jupiter.domain.prm.prm_database import PrmDatabase
from jupiter.domain.projects.project import Project
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase


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

    _storage_engine: Final[DomainStorageEngine]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'PrmDatabaseFindUseCase.Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            catch_up_project = uow.project_repository.load_by_id(prm_database.catch_up_project_ref_id)
            persons = uow.person_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_person_ref_ids)

        return self.Response(
            prm_database=prm_database,
            catch_up_project=catch_up_project,
            persons=persons)
