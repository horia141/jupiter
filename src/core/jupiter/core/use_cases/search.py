"""Use case for free form searching through Jupiter."""
from typing import Final, List, Optional

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search.infra.search_repository import SearchMatch
from jupiter.core.domain.search.search_limit import SearchLimit
from jupiter.core.domain.search.search_query import SearchQuery
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.use_case_io import (
    use_case_result,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args
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
    include_archived: bool = False
    filter_entity_tags: Optional[List[NamedEntityTag]] = None
    filter_created_time_after: Optional[ADate] = None
    filter_created_time_before: Optional[ADate] = None
    filter_last_modified_time_after: Optional[ADate] = None
    filter_last_modified_time_before: Optional[ADate] = None
    filter_archived_time_after: Optional[ADate] = None
    filter_archived_time_before: Optional[ADate] = None


@use_case_result
class SearchResult(UseCaseResultBase):
    """Search result."""

    matches: List[SearchMatch]


@readonly_use_case()
class SearchUseCase(AppLoggedInReadonlyUseCase[SearchArgs, SearchResult]):
    """Use case for free form searching through Jupiter."""

    _search_storage_engine: Final[SearchStorageEngine]

    def __init__(
        self,
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(
            auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
        )
        self._search_storage_engine = search_storage_engine

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

        return SearchResult(matches=matches)
