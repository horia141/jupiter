"""Command for showing the big plans."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.big_plans import BigPlansController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class BigPlansShow(command.Command):
    """Command class for showing the big plans."""

    _basic_validator: Final[BasicValidator]
    _big_plans_controller: Final[BigPlansController]

    def __init__(
            self, basic_validator: BasicValidator, big_plans_controller: BigPlansController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._big_plans_controller = big_plans_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plans-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of big plans"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the vacations to modify")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]\
            if len(args.ref_ids) > 0 else None
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys]\
            if len(args.project_keys) > 0 else None
        response = self._big_plans_controller.load_all_big_plans(
            filter_ref_ids=ref_ids, filter_project_keys=project_keys)

        for big_plan_entry in response.big_plans:
            big_plan = big_plan_entry.big_plan
            inbox_tasks = big_plan_entry.inbox_tasks
            print(f'id={big_plan.ref_id} {big_plan.name}' +
                  f' status={big_plan.status.value}' +
                  f' archived="{big_plan.archived}"' +
                  f' due_date="{self._basic_validator.adate_to_user(big_plan.due_date)}"')
            print("  Tasks:")
            for inbox_task in inbox_tasks:
                print(f'   - id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      f' due_date="{self._basic_validator.adate_to_user(inbox_task.due_date)}"')
