"""Command for creating big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.adate import ADate
from domain.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from use_cases.big_plans.create import BigPlanCreateCommand
from utils.global_properties import GlobalProperties


class BigPlanCreate(command.Command):
    """Command class for creating big plans."""

    _global_properties: Final[GlobalProperties]
    _command: Final[BigPlanCreateCommand]

    def __init__(self, global_properties: GlobalProperties, the_command: BigPlanCreateCommand) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a big plan"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=False,
                            help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the big plan")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = ProjectKey.from_raw(args.project_key) if args.project_key else None
        name = EntityName.from_raw(args.name)
        due_date = ADate.from_raw(self._global_properties.timezone, args.due_date) if args.due_date else None
        self._command.execute(BigPlanCreateCommand.Args(project_key, name, due_date))
