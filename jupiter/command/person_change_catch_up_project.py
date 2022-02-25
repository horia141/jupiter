"""UseCase for updating the person database."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.command.command import Command
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.persons.change_catch_up_project import PersonChangeCatchUpProjectUseCase


class PersonChangeCatchUpProject(Command):
    """UseCase for updating the person database."""

    _command: Final[PersonChangeCatchUpProjectUseCase]

    def __init__(self, the_command: PersonChangeCatchUpProjectUseCase):
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-change-catch-up-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the catch up project"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        catch_up_project_group = parser.add_mutually_exclusive_group()
        catch_up_project_group.add_argument(
            "--catch-up-project", dest="catch_up_project_key", required=False,
            help="The project key to generate recurring catch up tasks")
        catch_up_project_group.add_argument(
            "--clear-catch-up-project", dest="clear_catch_up_project_key",
            required=False, default=False, action="store_const", const=True,
            help="Clear the catch up project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        catch_up_project_key: Optional[ProjectKey]
        if args.clear_catch_up_project_key:
            catch_up_project_key = None
        else:
            catch_up_project_key = ProjectKey.from_raw(args.catch_up_project_key)

        self._command.execute(PersonChangeCatchUpProjectUseCase.Args(catch_up_project_key=catch_up_project_key))
