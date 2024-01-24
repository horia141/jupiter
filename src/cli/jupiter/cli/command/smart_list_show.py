"""UseCase for showing a smart list."""
from typing import List, cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.use_cases.smart_lists.find import (
    SmartListFindResult,
    SmartListFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class SmartListShow(LoggedInReadonlyCommand[SmartListFindUseCase]):
    """UseCase for showing the smart list."""

    def _render_result(self, result: SmartListFindResult) -> None:
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
