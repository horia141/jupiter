"""The command for finding the PRM database."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.domain.prm.person import Person
from jupiter.domain.prm.prm_database import PrmDatabase
from jupiter.domain.projects.project import Project
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppUseCaseContext, AppReadonlyUseCase


class PrmDatabaseFindUseCase(AppReadonlyUseCase['PrmDatabaseFindUseCase.Args', 'PrmDatabaseFindUseCase.Result']):
    """The command for finding the PRM Database."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        allow_archived: bool
        filter_person_ref_ids: Optional[List[EntityId]]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result."""

        prm_database: PrmDatabase
        catch_up_project: Project
        persons: List[Person]

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'PrmDatabaseFindUseCase.Result':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            prm_database = uow.prm_database_repository.load()
            catch_up_project = uow.project_repository.load_by_id(prm_database.catch_up_project_ref_id)
            persons = uow.person_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_person_ref_ids)

        return self.Result(
            prm_database=prm_database,
            catch_up_project=catch_up_project,
            persons=persons)
