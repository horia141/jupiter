"""Module for command base class"""

import abc


class Command(abc.ABC):
    """The base class for command"""

    @staticmethod
    @abc.abstractmethod
    def name():
        """The name of the command"""

    @staticmethod
    @abc.abstractmethod
    def description():
        """The description of the command"""

    @abc.abstractmethod
    def build_parser(self, parser):
        """Construct a argparse parser for the command"""

    @abc.abstractmethod
    def run(self, args):
        """Callback to execute when the command is invoked"""
