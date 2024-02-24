"""The command for creating a smart list tag."""

from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class SmartListTagCreateArgs(UseCaseArgsBase):
    """SmartListTagCreate args."""

    smart_list_ref_id: EntityId
    tag_name: TagName


@use_case_result
class SmartListTagCreateResult(UseCaseResultBase):
    """SmartListTagCreate result."""

    new_smart_list_tag: SmartListTag


@mutation_use_case(WorkspaceFeature.SMART_LISTS)
class SmartListTagCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        SmartListTagCreateArgs, SmartListTagCreateResult
    ],
):
    """The command for creating a smart list tag."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SmartListTagCreateArgs,
    ) -> SmartListTagCreateResult:
        """Execute the command's action."""
        metric = await uow.repository_for(SmartList).load_by_id(
            args.smart_list_ref_id,
        )
        new_smart_list_tag = SmartListTag.new_smart_list_tag(
            ctx=context.domain_context,
            smart_list_ref_id=metric.ref_id,
            tag_name=args.tag_name,
        )
        new_smart_list_tag = await uow.repository_for(SmartListTag).create(
            new_smart_list_tag,
        )
        await progress_reporter.mark_created(new_smart_list_tag)

        return SmartListTagCreateResult(new_smart_list_tag=new_smart_list_tag)
