"""UseCase for creating a smart list tag."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.tag.create import (
    SmartListTagCreateArgs,
    SmartListTagCreateUseCase,
)


class SmartListTagCreate(LoggedInMutationCommand[SmartListTagCreateUseCase]):
    """UseCase for creating a smart list tag."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list-id",
            dest="smart_list_ref_id",
            required=True,
            help="The key of the smart list to add the tag to",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the smart list",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_ref_id = EntityId.from_raw(args.smart_list_ref_id)
        tag_name = SmartListTagName.from_raw(args.name)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListTagCreateArgs(
                smart_list_ref_id=smart_list_ref_id, tag_name=tag_name
            ),
        )
