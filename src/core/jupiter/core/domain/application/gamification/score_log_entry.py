"""A particular entry in the score log related to an task being completed."""

import abc
import random

from jupiter.core.domain.application.gamification.score_source import ScoreSource
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
)
from jupiter.core.framework.repository import LeafEntityRepository


@entity
class ScoreLogEntry(LeafEntity):
    """A record of a win or loss in accomplishing a task."""

    score_log: ParentLink
    source: ScoreSource
    task_ref_id: EntityId
    difficulty: Difficulty | None
    success: bool
    has_lucky_puppy_bonus: bool | None
    score: int

    @staticmethod
    @create_entity_action
    def new_from_inbox_task(
        ctx: DomainContext,
        score_log_ref_id: EntityId,
        inbox_task: InboxTask,
    ) -> "ScoreLogEntry":
        """Create an entry from an inbox task."""
        if not inbox_task.status.is_completed:
            raise Exception(
                "Cannot create score logs for inbox tasks that are not complete!"
            )

        has_lucky_puppy_bonus = None
        if inbox_task.status == InboxTaskStatus.DONE:
            has_lucky_puppy_bonus = random.randint(0, 99) < 10  # nosec

        return ScoreLogEntry._create(
            ctx,
            name=EntityName(f"For InboxTask #{inbox_task.ref_id} '{inbox_task.name}'"),
            score_log=ParentLink(score_log_ref_id),
            source=ScoreSource.INBOX_TASK,
            task_ref_id=inbox_task.ref_id,
            difficulty=inbox_task.difficulty,
            success=inbox_task.status == InboxTaskStatus.DONE,
            has_lucky_puppy_bonus=has_lucky_puppy_bonus,
            score=ScoreLogEntry._compute_score_for_inbox_task(
                inbox_task, has_lucky_puppy_bonus
            ),
        )

    @staticmethod
    @create_entity_action
    def new_from_big_plan(
        ctx: DomainContext,
        score_log_ref_id: EntityId,
        big_plan: BigPlan,
    ) -> "ScoreLogEntry":
        """Create an entry from an inbox task."""
        if not big_plan.status.is_completed:
            raise Exception(
                "Cannot create score logs for big plans that are not completed!e"
            )

        return ScoreLogEntry._create(
            ctx,
            name=EntityName(f"For BigPlan #{big_plan.ref_id} '{big_plan.name}'"),
            score_log=ParentLink(score_log_ref_id),
            source=ScoreSource.BIG_PLAN,
            task_ref_id=big_plan.ref_id,
            difficulty=None,
            success=big_plan.status == BigPlanStatus.DONE,
            has_lucky_puppy_bonus=None,
            score=ScoreLogEntry._compute_score_for_big_plan(big_plan),
        )

    @staticmethod
    def _compute_score_for_inbox_task(
        inbox_task: InboxTask, has_lucky_puppy_bonus: bool | None
    ) -> int:
        lucky_puppy_modifier = 1 if has_lucky_puppy_bonus else 0
        if inbox_task.status == InboxTaskStatus.DONE:
            if inbox_task.difficulty == Difficulty.EASY:
                return 1 + lucky_puppy_modifier
            elif inbox_task.difficulty == Difficulty.MEDIUM:
                return 2 + lucky_puppy_modifier
            else:  # inbox_task.difficulty == Difficulty.HARD:
                return 5 + lucky_puppy_modifier
        else:  # inbox_task.status == InboxTaskStatus.NOT_DONE:
            if inbox_task.difficulty == Difficulty.EASY:
                return -1
            elif inbox_task.difficulty == Difficulty.MEDIUM:
                return -2
            else:  # inbox_task.difficulty == Difficulty.HARD:
                return -5

    @staticmethod
    def _compute_score_for_big_plan(big_plan: BigPlan) -> int:
        if big_plan.status == BigPlanStatus.DONE:
            if big_plan.difficulty == Difficulty.EASY:
                return 10
            elif big_plan.difficulty == Difficulty.MEDIUM:
                return 25
            else:  # big_plan.difficulty == Difficulty.HARD:
                return 50
        else:  # big_plan.status == BigPlanStatus.NOT_DONE:
            if big_plan.difficulty == Difficulty.EASY:
                return -10
            elif big_plan.difficulty == Difficulty.MEDIUM:
                return -25
            else:  # big_plan.difficulty == Difficulty.HARD:
                return -50


class ScoreLogEntryRepository(LeafEntityRepository[ScoreLogEntry], abc.ABC):
    """A repository of score log entries."""
