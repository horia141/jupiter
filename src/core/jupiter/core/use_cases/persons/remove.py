"""Remove a person."""
from dataclasses import dataclass

from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class PersonRemoveUseCase(AppLoggedInMutationUseCase[PersonRemoveArgs, None]):
    """The command for removing a person."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            person = await uow.person_repository.load_by_id(
                args.ref_id,
                allow_archived=True,
            )

        await PersonRemoveService(
            self._storage_engine,
        ).do_it(progress_reporter, person_collection, person)
