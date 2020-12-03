"""Command for syncing the local and Notion-side data."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.sync_local_and_notion import SyncLocalAndNotionController
from models.basic import BasicValidator, SyncPrefer, SyncTarget

LOGGER = logging.getLogger(__name__)


class SyncLocalAndNotion(command.Command):
    """Command class for syncing the local and Notion-side data."""

    _basic_validator: Final[BasicValidator]
    _sync_local_and_notion_controller: Final[SyncLocalAndNotionController]

    def __init__(
            self, basic_validator: BasicValidator,
            sync_local_and_notion_controller: SyncLocalAndNotionController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._sync_local_and_notion_controller = sync_local_and_notion_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "sync"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Sync the local and Notion-side data"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--target", dest="sync_targets", default=[], action="append",
                            choices=BasicValidator.sync_target_values(), help="What exactly to try to sync")
        parser.add_argument("--vacation-id", dest="vacation_ref_ids", default=[], action="append",
                            help="Sync only from this vacation")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Sync only from this project")
        parser.add_argument("--inbox-task-id", dest="inbox_task_ref_ids", default=[], action="append",
                            help="Sync only these particular tasks")
        parser.add_argument("--big-plan-id", dest="big_plan_ref_ids", default=[], action="append",
                            help="Sync only these particular big plans")
        parser.add_argument("--recurring-task-id", dest="recurring_task_ref_ids", default=[], action="append",
                            help="Sync only these recurring tasks")
        parser.add_argument("--smart-list", dest="smart_list_keys", default=[], action="append",
                            help="Sync only these smart lists")
        parser.add_argument("--smart-list-item-id", dest="smart_list_item_ref_ids", default=[], action="append",
                            help="Sync only these smart list items")
        parser.add_argument("--prefer", dest="sync_prefer", choices=BasicValidator.sync_prefer_values(),
                            default=SyncPrefer.NOTION.value, help="Which source to prefer")
        parser.add_argument("--drop-all-notion", dest="drop_all_notion", action="store_true", default=False,
                            help="Drop all Notion-side entities before syncing and restore from local entirely")
        parser.add_argument("--ignore-modified-times", dest="sync_even_if_not_modified", action="store_true",
                            default=False, help="Drop all Notion-side archived")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        sync_targets = [self._basic_validator.sync_target_validate_and_clean(st) for st in args.sync_targets]\
            if len(args.sync_targets) > 0 else list(st for st in SyncTarget)
        vacation_ref_ids = [self._basic_validator.entity_id_validate_and_clean(v) for v in args.vacation_ref_ids] \
            if len(args.vacation_ref_ids) > 0 else None
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys]\
            if len(args.project_keys) > 0 else None
        inbox_task_ref_ids = [self._basic_validator.entity_id_validate_and_clean(bp)
                              for bp in args.inbox_task_ref_ids] \
            if len(args.inbox_task_ref_ids) > 0 else None
        big_plan_ref_ids = [self._basic_validator.entity_id_validate_and_clean(bp) for bp in args.big_plan_ref_ids] \
            if len(args.big_plan_ref_ids) > 0 else None
        recurring_task_ref_ids = [self._basic_validator.entity_id_validate_and_clean(rt)
                                  for rt in args.recurring_task_ref_ids] \
            if len(args.recurring_task_ref_ids) > 0 else None
        smart_list_keys = [self._basic_validator.smart_list_key_validate_and_clean(sl)
                           for sl in args.smart_list_keys] \
            if len(args.smart_list_keys) > 0 else None
        smart_list_item_ref_ids = [self._basic_validator.entity_id_validate_and_clean(sli)
                                   for sli in args.smart_list_item_ref_ids] \
            if len(args.smart_list_item_ref_ids) > 0 else None
        sync_prefer = self._basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)
        drop_all_notion = args.drop_all_notion
        sync_even_if_not_modified = args.sync_even_if_not_modified
        self._sync_local_and_notion_controller.sync(
            sync_targets=sync_targets,
            drop_all_notion=drop_all_notion,
            sync_even_if_not_modified=sync_even_if_not_modified,
            filter_vacation_ref_ids=vacation_ref_ids,
            filter_project_keys=project_keys,
            filter_inbox_task_ref_ids=inbox_task_ref_ids,
            filter_big_plan_ref_ids=big_plan_ref_ids,
            filter_recurring_task_ref_ids=recurring_task_ref_ids,
            filter_smart_list_keys=smart_list_keys,
            filter_smart_list_item_ref_ids=smart_list_item_ref_ids,
            sync_prefer=sync_prefer)
