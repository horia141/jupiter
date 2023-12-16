"""The command for removing a doc."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.docs.service.doc_remove_service import (
    DocRemoveService,
)
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
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
class DocRemoveArgs(UseCaseArgsBase):
    """DocRemove arguments."""

    ref_id: EntityId


class DocRemoveUseCase(AppTransactionalLoggedInMutationUseCase[DocRemoveArgs, None]):
    """The command for removing a doc."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.DOCS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: DocRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        await DocRemoveService().do_it(uow, progress_reporter, doc)
