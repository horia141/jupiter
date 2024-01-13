"""UseCase for updating a vacation's properties."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.vacations.update import (
    VacationUpdateArgs,
    VacationUpdateUseCase,
)
from jupiter.core.utils.global_properties import GlobalProperties


class VacationUpdate(LoggedInMutationCommand[VacationUpdateUseCase]):
    """UseCase for updating a vacation's properties."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: VacationUpdateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the vacation to modify",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the vacation",
        )
        parser.add_argument(
            "--start-date",
            dest="start_date",
            required=False,
            help="The vacation start date",
        )
        parser.add_argument(
            "--end-date",
            dest="end_date",
            required=False,
            help="The vacation end date",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name is not None:
            name = UpdateAction.change_to(VacationName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.start_date is not None:
            start_date = UpdateAction.change_to(
                ADate.from_raw_in_tz(self._global_properties.timezone, args.start_date),
            )
        else:
            start_date = UpdateAction.do_nothing()
        if args.end_date is not None:
            end_date = UpdateAction.change_to(
                ADate.from_raw_in_tz(self._global_properties.timezone, args.end_date),
            )
        else:
            end_date = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            VacationUpdateArgs(
                ref_id=ref_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
            ),
        )
