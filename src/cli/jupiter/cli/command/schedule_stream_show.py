"""Command for showing the schedule streams."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import entity_id_to_rich_text
from jupiter.core.use_cases.concept.schedule.stream.find import (
    ScheduleStreamFindResult,
    ScheduleStreamFindUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class ScheduleStreamShow(
    LoggedInReadonlyCommand[ScheduleStreamFindUseCase, ScheduleStreamFindResult]
):
    """Command class for showing the schedule streams."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: ScheduleStreamFindResult,
    ) -> None:
        rich_tree = Tree("📅 Schedule Streams", guide_style="bold bright_blue")

        for entry in result.entries:
            schedule_stream_text = Text("")
            schedule_stream_text.append(
                entity_id_to_rich_text(entry.schedule_stream.ref_id)
            )
            schedule_stream_text.append(" ")
            schedule_stream_text.append(
                f"{entry.schedule_stream.name}", style=entry.schedule_stream.color.value
            )

            rich_tree.add(schedule_stream_text)

        console.print(rich_tree)
