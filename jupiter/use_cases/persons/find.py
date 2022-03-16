"""The command for finding the persons."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.domain.persons.person import Person
from jupiter.domain.projects.project import Project
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppUseCaseContext, AppReadonlyUseCase


class PersonFindUseCase(AppReadonlyUseCase['PersonFindUseCase.Args', 'PersonFindUseCase.Result']):
    """The command for finding the persons."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        allow_archived: bool
        filter_person_ref_ids: Optional[List[EntityId]]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result."""

        catch_up_project: Project
        persons: List[Person]

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'PersonFindUseCase.Result':
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            person_collection = uow.person_collection_repository.load_by_parent(workspace.ref_id)
            catch_up_project = uow.project_repository.load_by_id(person_collection.catch_up_project_ref_id)
            persons = \
                uow.person_repository.find_all(
                    parent_ref_id=person_collection.ref_id,
                    allow_archived=args.allow_archived,
                    filter_ref_ids=args.filter_person_ref_ids)

        return self.Result(catch_up_project=catch_up_project, persons=persons)
