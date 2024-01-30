"""Command for logging out."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import Command
from jupiter.core.framework.secure import secure_class
from rich.console import Console


@secure_class
class Logout(Command):
    """Command for logging out."""

    def name(self) -> str:
        """The name of the command."""
        return "logout"

    def description(self) -> str:
        """The description of the command."""
        return "Logout of the application"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        self._session_storage.clear()

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False
