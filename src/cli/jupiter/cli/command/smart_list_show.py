"""UseCase for showing a smart list."""
from argparse import ArgumentParser, Namespace
from typing import List, cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.find import (
    SmartListFindArgs,
    SmartListFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class SmartListShow(LoggedInReadonlyCommand[SmartListFindUseCase]):
    """UseCase for showing the smart list."""

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
            "--id",
            dest="ref_ids",
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

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        filter_ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
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

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListFindArgs(
                allow_archived=show_archived,
                include_tags=True,
                include_items=True,
                filter_ref_ids=filter_ref_ids,
                filter_is_done=filter_is_done,
                filter_tag_names=filter_tag_names,
            ),
        )

        sorted_smart_lists = sorted(
            result.entries,
            key=lambda sl: (sl.smart_list.archived, sl.smart_list.created_time),
        )

        rich_tree = Tree("🏛️  Smart Lists", guide_style="bold bright_blue")

        for smart_list_entry in sorted_smart_lists:
            smart_list = smart_list_entry.smart_list
            smart_list_tags_set = {
                t.ref_id: t
                for t in cast(List[SmartListTag], smart_list_entry.smart_list_tags)
            }

            smart_list_text = Text("")
            smart_list_text.append(entity_id_to_rich_text(smart_list.ref_id))
            if smart_list.icon:
                smart_list_text.append(" ")
                smart_list_text.append(str(smart_list.icon))
            smart_list_text.append(" ")
            smart_list_text.append(str(smart_list.name))

            smart_list_info_text = Text("")

            for smart_list_tag in smart_list_tags_set.values():
                smart_list_info_text.append("<")
                smart_list_info_text.append(
                    entity_id_to_rich_text(smart_list_tag.ref_id),
                )
                smart_list_info_text.append(" ")
                smart_list_info_text.append(str(smart_list_tag.tag_name))
                smart_list_info_text.append("> ")

            if smart_list.archived:
                smart_list_text.stylize("gray62")
                smart_list_info_text.stylize("gray62")

            smart_list_tree = rich_tree.add(
                smart_list_text,
                guide_style="gray62" if smart_list.archived else "blue",
            )
            smart_list_tree.add(smart_list_info_text)

            for smart_list_item in cast(
                List[SmartListItem], smart_list_entry.smart_list_items
            ):
                smart_list_item_text = Text("")
                smart_list_item_text.append(
                    entity_id_to_rich_text(smart_list_item.ref_id),
                )
                smart_list_item_text.append(" ")
                smart_list_item_text.append(
                    entity_name_to_rich_text(smart_list_item.name),
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
