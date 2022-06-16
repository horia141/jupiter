"""Module for command base class."""

import abc
from argparse import ArgumentParser, Namespace


class Command(abc.ABC):
    """The base class for command."""

    @staticmethod
    @abc.abstractmethod
    def name() -> str:
        """The name of the command."""

    @staticmethod
    @abc.abstractmethod
    def description() -> str:
        """The description of the command."""

    @abc.abstractmethod
    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    @abc.abstractmethod
    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return True


class TestHelperCommand(Command, abc.ABC):
    """Base class for commands used in tests."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return False
