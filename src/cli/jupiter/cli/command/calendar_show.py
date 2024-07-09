"""Command for loading a calendar."""
from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.core.use_cases.application.calendar.load_for_date_and_period import (
    CalendarLoadForDateAndPeriodResult,
    CalendarLoadForDateAndPeriodUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console


class CalendarShow(
    LoggedInReadonlyCommand[
        CalendarLoadForDateAndPeriodUseCase, CalendarLoadForDateAndPeriodResult
    ]
):
    """Command for loading a calendar."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: CalendarLoadForDateAndPeriodResult,
    ) -> None:
        console.print(result)
