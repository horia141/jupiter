"""UseCase for showing the persons."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    period_to_rich_text,
    person_birthday_to_rich_text,
    person_relationship_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.features import Feature
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.persons.find import PersonFindArgs, PersonFindUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class PersonShow(LoggedInReadonlyCommand[PersonFindUseCase]):
    """UseCase for showing the persons."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "person-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the persons"

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
            type=str,
            dest="ref_ids",
            default=[],
            action="append",
            help="The id of the persons to show",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        ref_ids = (
            [EntityId.from_raw(rid) for rid in args.ref_ids]
            if len(args.ref_ids) > 0
            else None
        )

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            PersonFindArgs(
                allow_archived=show_archived,
                include_catch_up_inbox_tasks=False,
                include_birthday_inbox_tasks=False,
                filter_person_ref_ids=ref_ids,
            ),
        )

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

        if self._top_level_context.workspace.is_feature_available(Feature.PROJECTS):
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
