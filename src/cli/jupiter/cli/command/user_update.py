"""Command for updating the user."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.user.update import UserUpdateArgs, UserUpdateUseCase


class UserUpdate(LoggedInMutationCommand[UserUpdateUseCase]):
    """Command class for updating the user."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", required=False, help="The user name to use")
        parser.add_argument(
            "--timezone",
            required=False,
            help="The timezone you're currently in",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        if args.name is not None:
            name = UpdateAction.change_to(UserName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.timezone is not None:
            timezone = UpdateAction.change_to(Timezone.from_raw(args.timezone))
        else:
            timezone = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            UserUpdateArgs(name=name, timezone=timezone),
        )
