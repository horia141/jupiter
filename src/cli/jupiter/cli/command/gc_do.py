"""UseCase for archiving done tasks."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.event import EventSource
from jupiter.core.use_cases.gc.do import GCDoArgs, GCDoUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class GCDo(LoggedInMutationCommand[GCDoUseCase]):
    """UseCase class for archiving done tasks."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--target",
            dest="gc_targets",
            default=[],
            action="append",
            choices=[
                s.value
                for s in self._top_level_context.workspace.infer_sync_targets_for_enabled_features(
                    None
                )
            ],
            help="What exactly to try to sync",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        gc_targets = (
            [SyncTarget.from_raw(st) for st in args.gc_targets]
            if len(args.gc_targets) > 0
            else None
        )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            GCDoArgs(
                source=EventSource.CLI,
                gc_targets=gc_targets,
            ),
        )
