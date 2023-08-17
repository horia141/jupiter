"""Remove a person."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class PersonRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class PersonRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[PersonRemoveArgs, None]
):
    """The command for removing a person."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.PERSONS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        person_collection = await uow.person_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        person = await uow.person_repository.load_by_id(
            args.ref_id,
            allow_archived=True,
        )

        await PersonRemoveService().do_it(
            uow, progress_reporter, person_collection, person
        )
