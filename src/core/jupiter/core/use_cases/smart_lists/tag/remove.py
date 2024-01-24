"""The command for removing a smart list tag."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class SmartListTagRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListTagRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListTagRemoveArgs, None]
):
    """The command for removing a smart list tag."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListTagRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_tag = await uow.smart_list_tag_repository.load_by_id(args.ref_id)

        smart_list_items = await uow.smart_list_item_repository.find_all_with_filters(
            parent_ref_id=smart_list_tag.smart_list.ref_id,
            allow_archived=True,
            filter_tag_ref_ids=[args.ref_id],
        )

        for smart_list_item in smart_list_items:
            smart_list_item = smart_list_item.update(
                ctx=context.domain_context,
                name=UpdateAction.do_nothing(),
                is_done=UpdateAction.do_nothing(),
                tags_ref_id=UpdateAction.change_to(
                    [t for t in smart_list_item.tags_ref_id if t != args.ref_id],
                ),
                url=UpdateAction.do_nothing(),
            )
            await uow.smart_list_item_repository.save(smart_list_item)
            await progress_reporter.mark_updated(smart_list_item)

        await uow.smart_list_tag_repository.remove(args.ref_id)
        await progress_reporter.mark_removed(smart_list_tag)
