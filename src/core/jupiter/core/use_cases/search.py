"""Use case for free form searching through Jupiter."""
from dataclasses import dataclass
from typing import Final, List, Optional

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search_repository import SearchMatch
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class SearchArgs(UseCaseArgsBase):
    """Search args."""

    query: str
    limit: int
    include_archived: bool = False
    filter_entity_tags: Optional[List[NamedEntityTag]] = None


@dataclass
class SearchResult(UseCaseResultBase):
    """Search result."""

    matches: List[SearchMatch]


_MAX_QUERY_LIMIT = 100


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
        self, context: AppLoggedInUseCaseContext, args: SearchArgs
    ) -> SearchResult:
        """Execute the command's action."""
        workspace = context.workspace

        if args.limit < 1:
            raise InputValidationError("Limit needs to be at least 1")
        if args.limit > _MAX_QUERY_LIMIT:
            raise InputValidationError(
                f"Limit needs to be no more than {_MAX_QUERY_LIMIT}"
            )

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
                filter_entity_tags=args.filter_entity_tags,
            )

        return SearchResult(matches=matches)
