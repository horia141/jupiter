"""The command for updating a smart list tag."""

from jupiter.core.domain.concept.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.core.tags.tag_name import TagName
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
class SmartListTagUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    tag_name: UpdateAction[TagName]


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListTagUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SmartListTagUpdateArgs, None]
):
    """The command for updating a smart list tag."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListTagUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        smart_list_tag = await uow.get_for(SmartListTag).load_by_id(args.ref_id)
        smart_list_tag = smart_list_tag.update(
            ctx=context.domain_context,
            tag_name=args.tag_name,
        )

        await uow.get_for(SmartListTag).save(smart_list_tag)
        await progress_reporter.mark_updated(smart_list_tag)
