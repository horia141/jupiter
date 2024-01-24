"""UseCase for updating a smart list."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.update import (
    SmartListUpdateArgs,
    SmartListUpdateUseCase,
)


class SmartListUpdate(LoggedInMutationCommand[SmartListUpdateUseCase]):
    """UseCase for updating a smart list."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The key of the smart list",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the smart list",
        )
        icon = parser.add_mutually_exclusive_group()
        icon.add_argument(
            "--icon",
            dest="icon",
            help="The icon or :alias: for the smart list",
        )
        icon.add_argument(
            "--clear-icon",
            dest="clear_icon",
            default=False,
            action="store_const",
            const=True,
            help="Clear the icon and use the default one",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(SmartListName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        icon: UpdateAction[Optional[EntityIcon]]
        if args.clear_icon:
            icon = UpdateAction.change_to(None)
        elif args.icon:
            icon = UpdateAction.change_to(EntityIcon.from_raw(args.icon))
        else:
            icon = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListUpdateArgs(ref_id=ref_id, name=name, icon=icon),
        )
