"""The command for removing a doc."""
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.service.doc_remove_service import (
    DocRemoveService,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
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
class DocRemoveArgs(UseCaseArgsBase):
    """DocRemove arguments."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.DOCS, exclude_app=[EventSource.CLI])
class DocRemoveUseCase(AppTransactionalLoggedInMutationUseCase[DocRemoveArgs, None]):
    """The command for removing a doc."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: DocRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        doc = await uow.get_for(Doc).load_by_id(args.ref_id)
        await DocRemoveService().do_it(
            context.domain_context, uow, progress_reporter, doc
        )
