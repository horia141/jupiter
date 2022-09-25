"""UseCase for showing the vacations."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_id_to_rich_text,
    start_date_to_rich_text,
    end_date_to_rich_text,
    entity_name_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.vacations.find import VacationFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class VacationsShow(command.ReadonlyCommand):
    """UseCase class for showing the vacations."""

    _global_properties: Final[GlobalProperties]
    _command: Final[VacationFindUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: VacationFindUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of vacations"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_ids",
            default=[],
            action="append",
            required=False,
            help="Show only tasks selected by this id",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]

        result = self._command.execute(
            progress_reporter,
            VacationFindUseCase.Args(
                allow_archived=show_archived,
                filter_ref_ids=ref_ids if len(ref_ids) > 0 else None,
            ),
        )

        sorted_vacations = sorted(
            result.vacations,
            key=lambda v: (v.archived, v.start_date, v.end_date),
        )

        rich_tree = Tree("🌴 Vacations", guide_style="bold bright_blue")

        for vacation in sorted_vacations:
            vacation_text = Text("")
            vacation_text.append(entity_id_to_rich_text(vacation.ref_id))
            vacation_text.append(" ")
            vacation_text.append(entity_name_to_rich_text(vacation.name))
            vacation_text.append(" ")
            vacation_text.append(start_date_to_rich_text(vacation.start_date))
            vacation_text.append(" ")
            vacation_text.append(end_date_to_rich_text(vacation.end_date))

            if vacation.archived:
                vacation_text.stylize("gray62")

            rich_tree.add(vacation_text)

        console = Console()
        console.print(rich_tree)
