"""UseCase for updating big plans."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.concept.big_plans.update import (
    BigPlanUpdateResult,
    BigPlanUpdateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext
from rich.console import Console
from rich.text import Text


class BigPlanUpdate(LoggedInMutationCommand[BigPlanUpdateUseCase, BigPlanUpdateResult]):
    """UseCase class for updating big plans."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInMutationUseCaseContext,
        result: BigPlanUpdateResult,
    ) -> None:
        if result.record_score_result is not None:
            if result.record_score_result.latest_task_score > 0:
                color = "green"
                rich_text = Text("Congratulations! ")
            else:
                color = "red"
                rich_text = Text("Ah snap! ")

            points = (
                "points"
                if abs(result.record_score_result.latest_task_score) > 1
                else "point"
            )

            rich_text.append(
                f"You scored {result.record_score_result.latest_task_score} {points}. ",
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
