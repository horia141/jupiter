"""Command for running a pomodoro timer."""
import asyncio
from argparse import ArgumentParser, Namespace

import beepy
from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.utils.noop_use_case import NoOpUseCase
from rich.progress import Progress

_TIMER_SECONDS = 60 * 25


class Pomodoro(LoggedInReadonlyCommand[NoOpUseCase]):
    """Command for running a pomodoro timer."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "pomodoro"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Run a pomodoro timer"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        with Progress() as progress:
            task1 = progress.add_task("[red]Timer: ", total=_TIMER_SECONDS)

            for _i in range(_TIMER_SECONDS):
                await asyncio.sleep(1)
                progress.update(task1, advance=1)

        beepy.beep("success")
