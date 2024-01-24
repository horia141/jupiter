"""UseCase for updating a smart list tag."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.tag.update import (
    SmartListTagUpdateArgs,
    SmartListTagUpdateUseCase,
)


class SmartListTagUpdate(LoggedInMutationCommand[SmartListTagUpdateUseCase]):
    """UseCase for creating a smart list tag."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The id of the smart list tag",
        )
        parser.add_argument(
            "--name",
            dest="tag_name",
            required=False,
            help="The name of the smart list",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.tag_name:
            tag_name = UpdateAction.change_to(SmartListTagName.from_raw(args.tag_name))
        else:
            tag_name = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListTagUpdateArgs(ref_id=ref_id, tag_name=tag_name),
        )
