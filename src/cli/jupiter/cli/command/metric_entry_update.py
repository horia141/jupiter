"""UseCase for updating a metric entry's properties."""

from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.entry.update import (
    MetricEntryUpdateArgs,
    MetricEntryUpdateUseCase,
)


class MetricEntryUpdate(LoggedInMutationCommand[MetricEntryUpdateUseCase]):
    """UseCase for updating a metric entry's properties."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the metric",
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
            required=False,
            type=float,
            help="The value for the metric",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        collection_time = (
            UpdateAction.change_to(ADate.from_str(args.collection_time))
            if args.collection_time is not None
            else UpdateAction.do_nothing()
        )
        value = (
            UpdateAction.change_to(args.value)
            if args.value is not None
            else UpdateAction.do_nothing()
        )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricEntryUpdateArgs(
                ref_id=ref_id,
                collection_time=collection_time,
                value=value,
            ),
        )
