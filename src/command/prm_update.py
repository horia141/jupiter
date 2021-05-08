"""Command for updating the PRM database."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from command.command import Command
from domain.prm.commands.prm_database_update import PrmDatabaseUpdateCommand
from models.basic import BasicValidator, ProjectKey
from models.framework import UpdateAction


class PrmUpdate(Command):
    """Command for updating the PRM database."""

    _basic_validator: Final[BasicValidator]
    _command: Final[PrmDatabaseUpdateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: PrmDatabaseUpdateCommand):
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "prm-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update the PRM database"

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
        catch_up_project_key: UpdateAction[Optional[ProjectKey]]
        if args.clear_catch_up_project_key:
            catch_up_project_key = UpdateAction.change_to(None)
        elif args.catch_up_project_key is not None:
            catch_up_project_key = UpdateAction.change_to(
                self._basic_validator.project_key_validate_and_clean(args.catch_up_project_key))
        else:
            catch_up_project_key = UpdateAction.do_nothing()

        self._command.execute(PrmDatabaseUpdateCommand.Args(catch_up_project_key=catch_up_project_key))
