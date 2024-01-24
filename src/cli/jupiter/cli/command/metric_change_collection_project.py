"""UseCase for updating the metric collection project."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectArgs,
    MetricChangeCollectionProjectUseCase,
)


class MetricChangeCollectionProject(
    LoggedInMutationCommand[MetricChangeCollectionProjectUseCase]
):
    """Use case for updating the metric collection project."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        collection_project_group = parser.add_mutually_exclusive_group()
        collection_project_group.add_argument(
            "--collection-project-id",
            dest="collection_project_ref_id",
            required=False,
            help="The project key to generate collection tasks",
        )
        collection_project_group.add_argument(
            "--clear-collection-project",
            dest="clear_collection_project",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        collection_project_ref_id: Optional[EntityId]
        if args.clear_collection_project:
            collection_project_ref_id = None
        else:
            collection_project_ref_id = EntityId.from_raw(
                args.collection_project_ref_id
            )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricChangeCollectionProjectArgs(
                collection_project_ref_id=collection_project_ref_id,
            ),
        )
