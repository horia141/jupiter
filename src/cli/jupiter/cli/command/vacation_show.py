"""UseCase for showing the vacations."""


from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    end_date_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    start_date_to_rich_text,
)
from jupiter.core.use_cases.vacations.find import (
    VacationFindResult,
    VacationFindUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class VacationsShow(LoggedInReadonlyCommand[VacationFindUseCase]):
    """UseCase class for showing the vacations."""

    def _render_result(self, result: VacationFindResult) -> None:
        sorted_vacations = sorted(
            result.vacations,
            key=lambda v: (v.archived, v.start_date, v.end_date),
        )

        rich_tree = Tree("🌴 Vacations", guide_style="bold bright_blue")

        for vacation in sorted_vacations:
            vacation_text = Text("")
            vacation_text.append(entity_id_to_rich_text(vacation.ref_id))
            vacation_text.append(" ")
            vacation_text.append(entity_name_to_rich_text(vacation.name))
            vacation_text.append(" ")
            vacation_text.append(start_date_to_rich_text(vacation.start_date))
            vacation_text.append(" ")
            vacation_text.append(end_date_to_rich_text(vacation.end_date))

            if vacation.archived:
                vacation_text.stylize("gray62")

            rich_tree.add(vacation_text)

        console = Console()
        console.print(rich_tree)
