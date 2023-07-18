"""UseCase for adding a vacation."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.vacations.create import (
    VacationCreateArgs,
    VacationCreateUseCase,
)
from jupiter.core.utils.global_properties import GlobalProperties


class VacationCreate(LoggedInMutationCommand[VacationCreateUseCase]):
    """UseCase class for adding a vacation."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: VacationCreateUseCase,
    ):
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Add a new vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the vacation",
        )
        parser.add_argument(
            "--start-date",
            dest="start_date",
            required=True,
            help="The vacation start date",
        )
        parser.add_argument(
            "--end-date",
            dest="end_date",
            required=True,
            help="The vacation end date",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        name = VacationName.from_raw(args.name)
        start_date = ADate.from_raw(self._global_properties.timezone, args.start_date)
        end_date = ADate.from_raw(self._global_properties.timezone, args.end_date)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            VacationCreateArgs(name=name, start_date=start_date, end_date=end_date),
        )
