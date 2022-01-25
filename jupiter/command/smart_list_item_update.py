"""UseCase for updating a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

from jupiter.command import command
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.url import URL
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.use_cases.smart_lists.item.update import SmartListItemUpdateUseCase

LOGGER = logging.getLogger(__name__)


class SmartListItemUpdate(command.Command):
    """UseCase for updating a smart list item."""

    _command: Final[SmartListItemUpdateUseCase]

    def __init__(self, the_command: SmartListItemUpdateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True,
                            help="The smart list item to update")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list item")
        parser.add_argument("--done", dest="is_done", default=False, action="store_const", const=True,
                            help="Mark the smart list item as done")
        parser.add_argument("--not-done", dest="is_not_done", default=False, action="store_const", const=True,
                            help="Mark the smart list item as not done")
        parser.add_argument("--tag", dest="tags", default=[], action="append",
                            help="Tags for the smart list item")
        parser.add_argument("--url", dest="url", help="An url for the smart list item")
        parser.add_argument("--clear-url", dest="clear_url", default=False,
                            action="store_const", const=True, help="Clear the url")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(SmartListItemName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.is_done:
            is_done = UpdateAction.change_to(True)
        elif args.is_not_done:
            is_done = UpdateAction.change_to(False)
        else:
            is_done = UpdateAction.do_nothing()
        if len(args.tags) > 0:
            tags = UpdateAction.change_to([SmartListTagName.from_raw(t) for t in args.tags])
        else:
            tags = UpdateAction.do_nothing()
        url: UpdateAction[Optional[URL]]
        if args.clear_url:
            url = UpdateAction.change_to(None)
        elif args.url:
            url = UpdateAction.change_to(URL.from_raw(args.url))
        else:
            url = UpdateAction.do_nothing()
        self._command.execute(SmartListItemUpdateUseCase.Args(
            ref_id=ref_id, name=name, tags=tags, is_done=is_done, url=url))
