"""Update a doc use case."""

from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
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
class DocUpdateArgs(UseCaseArgsBase):
    """DocUpdate args."""

    ref_id: EntityId
    name: UpdateAction[DocName]


@mutation_use_case(WorkspaceFeature.DOCS, exclude_app=[EventSource.CLI])
class DocUpdateUseCase(AppTransactionalLoggedInMutationUseCase[DocUpdateArgs, None]):
    """Update a doc use case."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: DocUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        doc = doc.update(
            ctx=context.domain_context,
            name=args.name,
        )
        doc = await uow.doc_repository.save(doc)
        await progress_reporter.mark_updated(doc)
