"""Command for correcting the Notion-side structure."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.correct_notion_structure import CorrectNotionStructureController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class CorrectNotionStructure(command.Command):
    """Command class for correcting the Notion-side structure."""

    _basic_validator: Final[BasicValidator]
    _correct_structure_controller: Final[CorrectNotionStructureController]

    def __init__(
            self, basic_validator: BasicValidator,
            correct_structure_controller: CorrectNotionStructureController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._correct_structure_controller = correct_structure_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "correct-structure"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Correct the Notion-side structures"

    def build_parser(self, _parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        self._correct_structure_controller.correct_structure()
