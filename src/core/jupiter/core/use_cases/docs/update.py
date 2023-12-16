"""Update a doc use case."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class DocUpdateArgs(UseCaseArgsBase):
    """DocUpdate args."""

    ref_id: EntityId
    name: UpdateAction[DocName]


class DocUpdateUseCase(AppTransactionalLoggedInMutationUseCase[DocUpdateArgs, None]):
    """Update a doc use case."""

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
        args: DocUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        doc = doc.update(
            name=args.name,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        doc = await uow.doc_repository.save(doc)
        await progress_reporter.mark_updated(doc)
