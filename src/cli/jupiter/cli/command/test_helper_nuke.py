"""Test helper command for completely destroying a workspace."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.cli.command.command import TestHelperCommand
from jupiter.core.framework.use_case import EmptySession
from jupiter.core.use_cases.test_helper.nuke import NukeArgs, NukeUseCase


class TestHelperNuke(TestHelperCommand):
    """Test helper command for completely destroying a workspace."""

    _use_case: Final[NukeUseCase]

    def __init__(self, use_case: NukeUseCase) -> None:
        """Constructor."""
        self._use_case = use_case

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "test-helper-nuke"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Completely destroy a workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        await self._use_case.execute(EmptySession(), NukeArgs())
