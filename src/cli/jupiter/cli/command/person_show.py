"""UseCase for showing the persons."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    period_to_rich_text,
    person_birthday_to_rich_text,
    person_relationship_to_rich_text,
)
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.persons.find import PersonFindResult, PersonFindUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class PersonShow(LoggedInReadonlyCommand[PersonFindUseCase]):
    """UseCase for showing the persons."""

    def _render_result(self, result: PersonFindResult) -> None:
        sorted_entries = sorted(
            result.entries,
            key=lambda p: (
                p.person.archived,
                p.person.relationship,
                p.person.catch_up_params.period
                if p.person.catch_up_params
                else RecurringTaskPeriod.YEARLY,
            ),
        )

        rich_tree = Tree("👨 Persons", guide_style="bold bright_blue")

        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            catch_up_project_text = Text(
                f"The catch up project is {result.catch_up_project.name}",
            )
            rich_tree.add(catch_up_project_text)

        for entry in sorted_entries:
            person = entry.person
            person_text = entity_id_to_rich_text(person.ref_id)

            person_text.append(" ")
            person_text.append(entity_name_to_rich_text(person.name))

            person_text.append(" ")
            person_text.append(person_relationship_to_rich_text(person.relationship))

            if person.catch_up_params:
                person_text.append(" ")
                person_text.append(period_to_rich_text(person.catch_up_params.period))

            if person.birthday:
                person_text.append(" ")
                person_text.append(person_birthday_to_rich_text(person.birthday))

            if person.archived:
                person_text.stylize("gray62")

            rich_tree.add(person_text)

        console = Console()
        console.print(rich_tree)
