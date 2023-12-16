"""The command for changing the parent for a doc."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class DocChangeParentArgs(UseCaseArgsBase):
    """DocChangeParent arguments."""

    ref_id: EntityId
    parent_node_ref_id: EntityId | None


class DocChangeParentUseCase(
    AppTransactionalLoggedInMutationUseCase[DocChangeParentArgs, None]
):
    """The command for changing the parent for a doc ."""

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
        args: DocChangeParentArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        doc = doc.change_parent(
            args.parent_node_ref_id,
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.doc_repository.save(doc)
        await progress_reporter.mark_updated(doc)
