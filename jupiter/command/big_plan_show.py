"""UseCase for showing the big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

import jupiter.command.command as command
from jupiter.domain.adate import ADate
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.big_plans.find import BigPlanFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class BigPlanShow(command.Command):
    """UseCase class for showing the big plans."""

    _global_properties: Final[GlobalProperties]
    _command: Final[BigPlanFindUseCase]

    def __init__(
            self, global_properties: GlobalProperties, the_command: BigPlanFindUseCase) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "big-plan-show"

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
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]\
            if len(args.ref_ids) > 0 else None
        project_keys = [ProjectKey.from_raw(pk) for pk in args.project_keys] if len(args.project_keys) > 0 else None
        result = self._command.execute(BigPlanFindUseCase.Args(
            allow_archived=False, filter_ref_ids=ref_ids, filter_project_keys=project_keys))

        for big_plan_entry in result.big_plans:
            big_plan = big_plan_entry.big_plan
            inbox_tasks = big_plan_entry.inbox_tasks
            print(f'id={big_plan.ref_id} {big_plan.name}' +
                  f' status={big_plan.status.value}' +
                  f' archived="{big_plan.archived}"' +
                  f' due_date="{ADate.to_user_str(self._global_properties.timezone, big_plan.due_date)}"')
            print("  Tasks:")
            for inbox_task in inbox_tasks:
                print(f'   - id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      f' due_date="{ADate.to_user_str(self._global_properties.timezone, inbox_task.due_date)}"')
