"""UseCase for showing the vacations."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.core.framework.realm import RealmCodecRegistry

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    end_date_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    start_date_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.vacations.find import VacationFindArgs, VacationFindUseCase
from jupiter.core.utils.global_properties import GlobalProperties
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class VacationsShow(LoggedInReadonlyCommand[VacationFindUseCase]):
    """UseCase class for showing the vacations."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: VacationFindUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    # def build_parser(self, parser: ArgumentParser) -> None:
    #     """Construct a argparse parser for the command."""
    #     parser.add_argument(
    #         "--show-archived",
    #         dest="show_archived",
    #         default=False,
    #         action="store_true",
    #         help="Whether to show archived vacations or not",
    #     )
    #     parser.add_argument(
    #         "--id",
    #         type=str,
    #         dest="ref_ids",
    #         default=[],
    #         action="append",
    #         required=False,
    #         help="Show only tasks selected by this id",
    #     )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        allow_archived = args.allow_archived
        ref_ids = [EntityId.from_raw(rid) for rid in args.filter_ref_ids]

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            VacationFindArgs(
                allow_archived=allow_archived,
                filter_ref_ids=ref_ids if len(ref_ids) > 0 else None,
            ),
        )

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
