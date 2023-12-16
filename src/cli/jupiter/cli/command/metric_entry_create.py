"""UseCase for creating a metric entry."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.entry.create import (
    MetricEntryCreateArgs,
    MetricEntryCreateUseCase,
)


class MetricEntryCreate(LoggedInMutationCommand[MetricEntryCreateUseCase]):
    """UseCase for creating a metric entry."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--metric-id",
            dest="metric_ref_id",
            required=True,
            help="The key of the metric",
        )
        parser.add_argument(
            "--collection-time",
            dest="collection_time",
            required=False,
            help="The time at which a metric should be recorded",
        )
        parser.add_argument(
            "--value",
            dest="value",
            required=True,
            type=float,
            help="The value for the metric",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        metric_ref_id = EntityId.from_raw(args.metric_ref_id)
        collection_time = (
            ADate.from_str(args.collection_time) if args.collection_time else None
        )
        value = args.value

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricEntryCreateArgs(
                metric_ref_id=metric_ref_id,
                collection_time=collection_time,
                value=value,
            ),
        )
