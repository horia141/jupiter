"""Command for archiving done tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.garbage_collect_notion import GarbageCollectNotionController
from models.basic import BasicValidator, SyncTarget

LOGGER = logging.getLogger(__name__)


class GarbageCollect(command.Command):
    """Command class for archiving done tasks."""

    _basic_validator: Final[BasicValidator]
    _garbage_collect_notion_controller: Final[GarbageCollectNotionController]

    def __init__(
            self, basic_validator: BasicValidator,
            garbage_collect_notion_controller: GarbageCollectNotionController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._garbage_collect_notion_controller = garbage_collect_notion_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "gc"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Garbage collect the Notion-side"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--target", dest="sync_targets", default=[], action="append",
                            choices=BasicValidator.sync_target_values(), help="What exactly to try to sync")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")
        parser.add_argument("--no-archival", dest="do_archival", default=True, action="store_const", const=False,
                            help="Skip the archival phase")
        parser.add_argument("--no-anti-entropy", dest="do_anti_entropy", default=True, action="store_const",
                            const=False, help="Skip the anti-entropy fixing phase")
        parser.add_argument("--no-notion-cleanup", dest="do_notion_cleanup", default=True, action="store_const",
                            const=False, help="Skip the Notion cleanup phase")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        gc_targets = [self._basic_validator.sync_target_validate_and_clean(st) for st in args.sync_targets] \
            if len(args.sync_targets) > 0 else list(st for st in SyncTarget)
        project_keys = [self._basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys] \
            if len(args.project_keys) > 0 else None
        do_archival = args.do_archival
        do_anti_entropy = args.do_anti_entropy
        do_notion_cleanup = args.do_notion_cleanup
        self._garbage_collect_notion_controller.garbage_collect(
            gc_targets, project_keys, do_archival, do_anti_entropy, do_notion_cleanup)
