"""Command for showing the user."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    email_address_to_rich_text,
    entity_name_to_rich_text,
    timezone_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.user.load import UserLoadArgs, UserLoadUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class UserShow(LoggedInReadonlyCommand[UserLoadUseCase]):
    """Command class for showing the user."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "user-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the current information about the user"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            UserLoadArgs(),
        )

        rich_tree = Tree(f"⭐ {result.user.name}", guide_style="bold bright_blue")

        user_text = Text("")
        user_text.append(entity_name_to_rich_text(result.user.name))
        user_text.append(" ")
        user_text.append(email_address_to_rich_text(result.user.email_address))
        user_text.append(" ")
        user_text.append(timezone_to_rich_text(result.user.timezone))

        feature_flags_tree = Tree("Feature Flags:")
        for feature, flag in result.user.feature_flags.items():
            if flag:
                feature_flag_text = Text(f"✅ {feature}")
            else:
                feature_flag_text = Text(f"☑️ {feature}")
            feature_flags_tree.add(feature_flag_text)

        rich_tree.add(user_text)
        rich_tree.add(feature_flags_tree)

        console = Console()
        console.print(rich_tree)
