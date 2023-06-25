"""UseCase for creating a smart list item."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.item.create import (
    SmartListItemCreateArgs,
    SmartListItemCreateUseCase,
)


class SmartListItemCreate(LoggedInMutationCommand[SmartListItemCreateUseCase]):
    """UseCase for creating a smart list item."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--smart-list-id",
            dest="smart_list_ref_id",
            required=True,
            help="The key of the smart list to add the item to",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the smart list item",
        )
        parser.add_argument(
            "--done",
            dest="is_done",
            default=False,
            action="store_const",
            const=True,
            help="Mark the smart list item as done",
        )
        parser.add_argument(
            "--tag",
            dest="tag_names",
            default=[],
            action="append",
            help="Tags for the smart list item",
        )
        parser.add_argument("--url", dest="url", help="An url for the smart list item")

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_ref_id = EntityId.from_raw(args.smart_list_ref_id)
        name = SmartListItemName.from_raw(args.name)
        is_done = args.is_done
        tag_names = [SmartListTagName.from_raw(t) for t in args.tag_names]
        url = URL.from_raw(args.url) if args.url else None

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListItemCreateArgs(
                smart_list_ref_id=smart_list_ref_id,
                name=name,
                is_done=is_done,
                tag_names=tag_names,
                url=url,
            ),
        )
