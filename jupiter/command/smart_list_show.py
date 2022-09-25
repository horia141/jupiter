"""UseCase for showing a smart list."""
from argparse import Namespace, ArgumentParser
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_key_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.use_cases.smart_lists.find import SmartListFindUseCase


class SmartListShow(command.ReadonlyCommand):
    """UseCase for showing the smart list."""

    _command: Final[SmartListFindUseCase]

    def __init__(self, the_command: SmartListFindUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of smart lists"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )
        parser.add_argument(
            "--smart-list",
            dest="smart_list_keys",
            default=[],
            action="append",
            help="Allow only smart list items from this smart list",
        )
        parser.add_argument(
            "--done",
            dest="show_done",
            default=False,
            action="store_const",
            const=True,
            help="Show only smart list items which are done",
        )
        parser.add_argument(
            "--not-done",
            dest="show_not_done",
            default=False,
            action="store_const",
            const=True,
            help="Show only smart list items which are not done",
        )
        parser.add_argument(
            "--tag",
            dest="filter_tag_names",
            default=[],
            action="append",
            help="Allow only smart list items with this tag",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        keys = (
            [SmartListKey.from_raw(rid) for rid in args.smart_list_keys]
            if len(args.smart_list_keys) > 0
            else None
        )
        filter_is_done = None
        if args.show_done and not args.show_not_done:
            filter_is_done = True
        elif not args.show_done and args.show_not_done:
            filter_is_done = False
        filter_tag_names = (
            [SmartListTagName.from_raw(t) for t in args.filter_tag_names]
            if len(args.filter_tag_names) > 0
            else None
        )

        result = self._command.execute(
            progress_reporter,
            SmartListFindUseCase.Args(
                allow_archived=show_archived,
                filter_keys=keys,
                filter_is_done=filter_is_done,
                filter_tag_names=filter_tag_names,
            ),
        )

        sorted_smart_lists = sorted(
            result.smart_lists,
            key=lambda sl: (sl.smart_list.archived, sl.smart_list.created_time),
        )

        rich_tree = Tree("🏛️  Smart Lists", guide_style="bold bright_blue")

        for smart_list_entry in sorted_smart_lists:
            smart_list = smart_list_entry.smart_list
            smart_list_tags_set = {
                t.ref_id: t for t in smart_list_entry.smart_list_tags
            }

            smart_list_text = Text("")
            smart_list_text.append(entity_key_to_rich_text(smart_list.key))
            if smart_list.icon:
                smart_list_text.append(" ")
                smart_list_text.append(str(smart_list.icon))
            smart_list_text.append(" ")
            smart_list_text.append(str(smart_list.name))

            smart_list_info_text = Text("")

            for smart_list_tag in smart_list_tags_set.values():
                smart_list_info_text.append("<")
                smart_list_info_text.append(
                    entity_id_to_rich_text(smart_list_tag.ref_id)
                )
                smart_list_info_text.append(" ")
                smart_list_info_text.append(str(smart_list_tag.tag_name))
                smart_list_info_text.append("> ")

            if smart_list.archived:
                smart_list_text.stylize("gray62")
                smart_list_info_text.stylize("gray62")

            smart_list_tree = rich_tree.add(
                smart_list_text, guide_style="gray62" if smart_list.archived else "blue"
            )
            smart_list_tree.add(smart_list_info_text)

            for smart_list_item in smart_list_entry.smart_list_items:
                smart_list_item_text = Text("")
                smart_list_item_text.append(
                    entity_id_to_rich_text(smart_list_item.ref_id)
                )
                smart_list_item_text.append(" ")
                smart_list_item_text.append(
                    entity_name_to_rich_text(smart_list_item.name)
                )

                if smart_list_item.is_done:
                    smart_list_item_text.append(" ")
                    smart_list_item_text.append("✅")
                else:
                    smart_list_item_text.append(" ")
                    smart_list_item_text.append("🔲")

                if len(smart_list_item.tags_ref_id) > 0:
                    for tag_ref_id in smart_list_item.tags_ref_id:
                        tag = smart_list_tags_set[tag_ref_id]
                        smart_list_item_text.append(" #")
                        smart_list_item_text.append(str(tag.tag_name))

                if smart_list_item.url and str(smart_list_item.url) != "None":
                    smart_list_item_text.append(" ")
                    smart_list_item_text.append(str(smart_list_item.url))

                if smart_list_item.archived:
                    smart_list_info_text.stylize("gray62")

                smart_list_tree.add(smart_list_item_text)

        console = Console()
        console.print(rich_tree)
