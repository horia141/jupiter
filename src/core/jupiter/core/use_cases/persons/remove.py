"""Remove a person."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class PersonRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.PERSONS)
class PersonRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonRemoveArgs, None]
):
    """The command for removing a person."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: PersonRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        person = await uow.get_for(Person).load_by_id(
            args.ref_id,
            allow_archived=True,
        )

        await PersonRemoveService().do_it(
            context.domain_context, uow, progress_reporter, person_collection, person
        )
