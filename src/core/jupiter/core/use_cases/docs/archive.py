"""Use case for archiving a doc."""

from jupiter.core.domain.docs.service.doc_archive_service import DocArchiveService
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class DocArchiveArgs(UseCaseArgsBase):
    """DocArchive args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.DOCS)
class DocArchiveUseCase(AppTransactionalLoggedInMutationUseCase[DocArchiveArgs, None]):
    """Use case for archiving a doc."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: DocArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        await DocArchiveService().do_it(
            context.domain_context, uow, progress_reporter, doc
        )
