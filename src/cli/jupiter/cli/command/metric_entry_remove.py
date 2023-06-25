"""UseCase for hard removing a metric entry."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.entry.remove import (
    MetricEntryRemoveArgs,
    MetricEntryRemoveUseCase,
)


class MetricEntryRemove(LoggedInMutationCommand[MetricEntryRemoveUseCase]):
    """UseCase for hard removing a metric."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-entry-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a metric entry"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the metric entry",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricEntryRemoveArgs(ref_id=ref_id),
        )
