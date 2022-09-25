"""UseCase for showing the persons."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command.command import ReadonlyCommand
from jupiter.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    person_relationship_to_rich_text,
    period_to_rich_text,
    person_birthday_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.persons.find import PersonFindUseCase


class PersonShow(ReadonlyCommand):
    """UseCase for showing the persons."""

    _command: Final[PersonFindUseCase]

    def __init__(self, the_command: PersonFindUseCase):
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the persons"

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
            help="The id of the persons to show",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
            else None
        )

        result = self._command.execute(
            progress_reporter,
            PersonFindUseCase.Args(
                allow_archived=show_archived, filter_person_ref_ids=ref_ids
            ),
        )

        sorted_persons = sorted(
            result.persons,
            key=lambda p: (
                p.archived,
                p.relationship,
                p.catch_up_params.period
                if p.catch_up_params
                else RecurringTaskPeriod.YEARLY,
            ),
        )

        rich_tree = Tree("👨 Persons", guide_style="bold bright_blue")

        catch_up_project_text = Text(
            f"The catch up project is {result.catch_up_project.name}"
        )
        rich_tree.add(catch_up_project_text)

        for person in sorted_persons:
            person_text = entity_id_to_rich_text(person.ref_id)

            person_text.append(" ")
            person_text.append(entity_name_to_rich_text(person.name))

            person_text.append(" ")
            person_text.append(person_relationship_to_rich_text(person.relationship))

            if person.catch_up_params:
                person_text.append(" ")
                person_text.append(period_to_rich_text(person.catch_up_params.period))

            if person.birthday:
                person_text.append(" ")
                person_text.append(person_birthday_to_rich_text(person.birthday))

            if person.archived:
                person_text.stylize("gray62")

            rich_tree.add(person_text)

        console = Console()
        console.print(rich_tree)
