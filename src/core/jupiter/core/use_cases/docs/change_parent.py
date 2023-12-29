"""The command for changing the parent for a doc."""

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
class DocChangeParentArgs(UseCaseArgsBase):
    """DocChangeParent arguments."""

    ref_id: EntityId
    parent_node_ref_id: EntityId | None


@mutation_use_case(WorkspaceFeature.DOCS)
class DocChangeParentUseCase(
    AppTransactionalLoggedInMutationUseCase[DocChangeParentArgs, None]
):
    """The command for changing the parent for a doc ."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: DocChangeParentArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(args.ref_id)
        doc = doc.change_parent(
            context.domain_context,
            args.parent_node_ref_id,
        )
        await uow.doc_repository.save(doc)
        await progress_reporter.mark_updated(doc)
