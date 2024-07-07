"""Command for showing the calendar streams."""
from jupiter.core.use_cases.calendar.stream.find import CalendarStreamFindResult, CalendarStreamFindUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from jupiter.cli.command.rendering import entity_id_to_rich_text
from jupiter.cli.command.command import LoggedInReadonlyCommand
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class CalendarStreamShow(LoggedInReadonlyCommand[CalendarStreamFindUseCase, CalendarStreamFindResult]):
    """Command class for showing the calendar streams."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: CalendarStreamFindResult,
    ) -> None:
        rich_tree = Tree("📅 Calendar Streams", guide_style="bold bright_blue")

        for entry in result.entries:
            calendar_stream_text = Text("")
            calendar_stream_text.append(entity_id_to_rich_text(entry.calendar_stream.ref_id))
            calendar_stream_text.append(" ")
            calendar_stream_text.append(
                f"{entry.calendar_stream.name}", style=entry.calendar_stream.color.value
            )

            rich_tree.add(calendar_stream_text)

        console.print(rich_tree)
