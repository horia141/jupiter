"""UseCase for showing the persons."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command.command import Command
from jupiter.use_cases.persons.find import PersonFindUseCase
from jupiter.framework.base.entity_id import EntityId


class PersonShow(Command):
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
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the persons to show")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None

        response = self._command.execute(
            PersonFindUseCase.Args(allow_archived=False, filter_person_ref_ids=ref_ids))

        print(f"The catch up project is {response.catch_up_project.name}")

        print("Persons:")
        for person in response.persons:
            print(f" - {person.name} ({person.relationship.for_notion()})", end="")
            print(f" Catch up {person.catch_up_params.period.for_notion()}" if person.catch_up_params else "", end="")
            print(f" Birthday is {person.birthday}" if person.birthday else "")
