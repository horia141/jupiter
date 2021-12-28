"""UseCase for updating the PRM database."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.command.command import Command
from jupiter.use_cases.prm.update import PrmDatabaseUpdateUseCase
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.update_action import UpdateAction


class PrmUpdate(Command):
    """UseCase for updating the PRM database."""

    _command: Final[PrmDatabaseUpdateUseCase]

    def __init__(self, the_command: PrmDatabaseUpdateUseCase):
        """Constructor."""
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
            catch_up_project_key = UpdateAction.change_to(ProjectKey.from_raw(args.catch_up_project_key))
        else:
            catch_up_project_key = UpdateAction.do_nothing()

        self._command.execute(PrmDatabaseUpdateUseCase.Args(catch_up_project_key=catch_up_project_key))
