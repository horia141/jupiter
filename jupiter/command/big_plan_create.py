"""UseCase for creating big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.big_plans.create import BigPlanCreateUseCase
from jupiter.utils.global_properties import GlobalProperties


class BigPlanCreate(command.Command):
    """UseCase class for creating big plans."""

    _global_properties: Final[GlobalProperties]
    _command: Final[BigPlanCreateUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: BigPlanCreateUseCase
    ) -> None:
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
        parser.add_argument(
            "--project",
            dest="project_key",
            required=False,
            help="The key of the project",
        )
        parser.add_argument(
            "--name", dest="name", required=True, help="The name of the big plan"
        )
        parser.add_argument(
            "--actionable-date",
            dest="actionable_date",
            help="The actionable date of the big plan",
        )
        parser.add_argument(
            "--due-date", dest="due_date", help="The due date of the big plan"
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = (
            ProjectKey.from_raw(args.project_key) if args.project_key else None
        )
        name = BigPlanName.from_raw(args.name)
        actionable_date = (
            ADate.from_raw(self._global_properties.timezone, args.actionable_date)
            if args.actionable_date
            else None
        )
        due_date = (
            ADate.from_raw(self._global_properties.timezone, args.due_date)
            if args.due_date
            else None
        )
        self._command.execute(
            BigPlanCreateUseCase.Args(project_key, name, actionable_date, due_date)
        )
