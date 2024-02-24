"""The command for archiving a smart list."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
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
class SmartListArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListArchiveArgs, None]
):
    """The command for archiving a smart list."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list = await uow.repository_for(SmartList).load_by_id(args.ref_id)

        smart_list_tags = await uow.repository_for(SmartListTag).find_all(
            smart_list.ref_id,
        )
        smart_list_items = await uow.repository_for(SmartListItem).find_all(
            smart_list.ref_id,
        )

        for smart_list_tag in smart_list_tags:
            smart_list_tag = smart_list_tag.mark_archived(context.domain_context)
            await uow.repository_for(SmartListTag).save(smart_list_tag)
            await progress_reporter.mark_updated(smart_list_tag)

        for smart_list_item in smart_list_items:
            smart_list_item = smart_list_item.mark_archived(context.domain_context)
            await uow.repository_for(SmartListItem).save(smart_list_item)
            await progress_reporter.mark_updated(smart_list_item)

        smart_list = smart_list.mark_archived(context.domain_context)
        await uow.repository_for(SmartList).save(smart_list)
        await progress_reporter.mark_updated(smart_list)
