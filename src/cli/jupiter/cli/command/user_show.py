"""Command for showing the user."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    email_address_to_rich_text,
    entity_name_to_rich_text,
    timezone_to_rich_text,
    user_score_overview_to_rich,
)
from jupiter.core.use_cases.concept.users.load import UserLoadResult, UserLoadUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class UserShow(LoggedInReadonlyCommand[UserLoadUseCase, UserLoadResult]):
    """Command class for showing the user."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: UserLoadResult,
    ) -> None:
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

        if result.user_score_overview is not None:
            rich_tree.add(user_score_overview_to_rich(result.user_score_overview))

        console.print(rich_tree)
