"""Use case for archiving a doc."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.docs.service.doc_archive_service import DocArchiveService
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class DocArchiveArgs(UseCaseArgsBase):
    """DocArchive args."""

    ref_id: EntityId


class DocArchiveUseCase(AppTransactionalLoggedInMutationUseCase[DocArchiveArgs, None]):
    """Use case for archiving a doc."""

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
        args: DocArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        await DocArchiveService(
            EventSource.CLI,
            self._time_provider,
        ).do_it(uow, progress_reporter, doc)
