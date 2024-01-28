"""UseCase for updating inbox tasks."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.update import (
    InboxTaskUpdateResult,
    InboxTaskUpdateUseCase,
)
from rich.console import Console
from rich.text import Text


class InboxTaskUpdate(LoggedInMutationCommand[InboxTaskUpdateUseCase]):
    """UseCase class for updating inbox tasks."""

    def _render_result(self, console: Console, result: InboxTaskUpdateResult) -> None:
        if result.record_score_result is not None:
            if result.record_score_result.latest_task_score > 0:
                color = "green"
                rich_text = Text("⭐ Great! You scored ")
            else:
                color = "red"
                rich_text = Text("😿 snap! You lost ")

            points = (
                "points"
                if abs(result.record_score_result.latest_task_score) > 1
                else "point"
            )

            rich_text.append(
                f"{abs(result.record_score_result.latest_task_score)} {points}! ",
                style=f"bold {color}",
            )
            if result.record_score_result.has_lucky_puppy_bonus:
                rich_text.append(
                    "You got a 🐶lucky puppy🐶 bonus! ",
                    style="bold green",
                )
            rich_text.append(
                f"Which brings your total for today to {result.record_score_result.score_overview.daily_score} and for this week to {result.record_score_result.score_overview.weekly_score}."
            )

            self.mark_postscript(rich_text)
