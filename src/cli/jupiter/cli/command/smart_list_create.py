"""UseCase for creating a smart list."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.create import (
    SmartListCreateArgs,
    SmartListCreateUseCase,
)


class SmartListCreate(LoggedInMutationCommand[SmartListCreateUseCase]):
    """UseCase for creating a smart list."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the smart list",
        )
        parser.add_argument(
            "--icon",
            dest="icon",
            required=False,
            help="A unicode icon or :alias: for the smart list",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        name = SmartListName.from_raw(args.name)
        icon = EntityIcon.from_raw(args.icon) if args.icon else None

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListCreateArgs(name=name, icon=icon),
        )
