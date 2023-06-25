"""UseCase for updating a smart list item."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.smart_lists.item.update import (
    SmartListItemUpdateArgs,
    SmartListItemUpdateUseCase,
)


class SmartListItemUpdate(LoggedInMutationCommand[SmartListItemUpdateUseCase]):
    """UseCase for updating a smart list item."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The smart list item to update",
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
            "--not-done",
            dest="is_not_done",
            default=False,
            action="store_const",
            const=True,
            help="Mark the smart list item as not done",
        )
        parser.add_argument(
            "--tag",
            dest="tags",
            default=[],
            action="append",
            help="Tags for the smart list item",
        )
        parser.add_argument("--url", dest="url", help="An url for the smart list item")
        parser.add_argument(
            "--clear-url",
            dest="clear_url",
            default=False,
            action="store_const",
            const=True,
            help="Clear the url",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(SmartListItemName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.is_done:
            is_done = UpdateAction.change_to(True)
        elif args.is_not_done:
            is_done = UpdateAction.change_to(False)
        else:
            is_done = UpdateAction.do_nothing()
        if len(args.tags) > 0:
            tags = UpdateAction.change_to(
                [SmartListTagName.from_raw(t) for t in args.tags],
            )
        else:
            tags = UpdateAction.do_nothing()
        url: UpdateAction[Optional[URL]]
        if args.clear_url:
            url = UpdateAction.change_to(None)
        elif args.url:
            url = UpdateAction.change_to(URL.from_raw(args.url))
        else:
            url = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SmartListItemUpdateArgs(
                ref_id=ref_id,
                name=name,
                tags=tags,
                is_done=is_done,
                url=url,
            ),
        )
