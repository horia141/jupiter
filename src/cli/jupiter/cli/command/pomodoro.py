"""Command for running a pomodoro timer."""
import asyncio
from argparse import Namespace

import beepy
from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.utils.noop_use_case import NoOpUseCase
from rich.console import Console
from rich.progress import Progress

_TIMER_SECONDS = 60 * 25


class Pomodoro(LoggedInReadonlyCommand[NoOpUseCase, None]):
    """Command for running a pomodoro timer."""

    async def _run(
        self,
        console: Console,
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
