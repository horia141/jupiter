"""Use case for free form searching through jupiter."""

from jupiter.core.domain.application.search.infra.search_repository import SearchMatch
from jupiter.core.domain.application.search.search_limit import SearchLimit
from jupiter.core.domain.application.search.search_query import SearchQuery
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)


@use_case_args
class SearchArgs(UseCaseArgsBase):
    """Search args."""

    query: SearchQuery
    limit: SearchLimit
    include_archived: bool
    filter_entity_tags: list[NamedEntityTag] | None
    filter_created_time_after: ADate | None
    filter_created_time_before: ADate | None
    filter_last_modified_time_after: ADate | None
    filter_last_modified_time_before: ADate | None
    filter_archived_time_after: ADate | None
    filter_archived_time_before: ADate | None


@use_case_result
class SearchResult(UseCaseResultBase):
    """Search result."""

    search_time: ADate
    matches: list[SearchMatch]


@readonly_use_case()
class SearchUseCase(AppLoggedInReadonlyUseCase[SearchArgs, SearchResult]):
    """Use case for free form searching through jupiter."""

    async def _execute(
        self, context: AppLoggedInReadonlyUseCaseContext, args: SearchArgs
    ) -> SearchResult:
        """Execute the command's action."""
        workspace = context.workspace

        filter_entity_tags = (
            args.filter_entity_tags
            if args.filter_entity_tags is not None
            else workspace.infer_entity_tags_for_enabled_features(None)
        )
        filter_entity_tags_diff = list(
            set(filter_entity_tags).difference(
                workspace.infer_entity_tags_for_enabled_features(filter_entity_tags)
            )
        )
        if len(filter_entity_tags_diff) > 0:
            raise FeatureUnavailableError(
                f"Entities {','.join(s.value for s in filter_entity_tags_diff)} are not supported in this workspace"
            )

        async with self._search_storage_engine.get_unit_of_work() as uow:
            matches = await uow.search_repository.search(
                workspace_ref_id=workspace.ref_id,
                query=args.query,
                limit=args.limit,
                include_archived=args.include_archived,
                filter_entity_tags=filter_entity_tags,
                filter_created_time_after=args.filter_created_time_after,
                filter_created_time_before=args.filter_created_time_before,
                filter_last_modified_time_after=args.filter_last_modified_time_after,
                filter_last_modified_time_before=args.filter_last_modified_time_before,
                filter_archived_time_after=args.filter_archived_time_after,
                filter_archived_time_before=args.filter_archived_time_before,
            )

        return SearchResult(
            search_time=self._time_provider.get_current_date(),
            matches=matches,
        )
