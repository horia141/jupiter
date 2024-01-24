"""UseCase for updating big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.core.framework.realm import RealmCodecRegistry

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.big_plans.update import (
    BigPlanUpdateArgs,
    BigPlanUpdateResult,
    BigPlanUpdateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties
from rich.text import Text


class BigPlanUpdate(LoggedInMutationCommand[BigPlanUpdateUseCase]):
    """UseCase class for updating big plans."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: BigPlanUpdateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    def _render_result(self, result: BigPlanUpdateResult) -> None:
        if result.record_score_result is not None:
            if result.record_score_result.latest_task_score > 0:
                color = "green"
                rich_text = Text("Congratulations! ")
            else:
                color = "red"
                rich_text = Text("Ah snap! ")

            points = (
                "points"
                if abs(result.record_score_result.latest_task_score) > 1
                else "point"
            )

            rich_text.append(
                f"You scored {result.record_score_result.latest_task_score} {points}. ",
                style=f"bold {color}",
            )
            if result.record_score_result.has_lucky_puppy_bonus:
                rich_text.append(
                    "You got a 🐶lucky puppy🐶 bonus! ",
                    style="bold green",
                )
            rich_text.append(
                f"Which brings your total for today to {result.record_score_result.score_overview.daily_score} and for this week to {result.record_score_result.score_overview.weekly_score}."
            )

            self.mark_postscript(rich_text)
