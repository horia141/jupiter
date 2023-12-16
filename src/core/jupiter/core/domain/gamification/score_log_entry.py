"""A particular entry in the score log related to an task being completed."""
import random
from dataclasses import dataclass

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.gamification.score_source import ScoreSource
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.event import EventSource


@dataclass
class ScoreLogEntry(LeafEntity):
    """A record of a win or loss in accomplishing a task."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    score_log_ref_id: EntityId
    source: ScoreSource
    task_ref_id: EntityId
    difficulty: Difficulty | None
    success: bool
    has_lucky_puppy_bonus: bool | None
    score: int

    @staticmethod
    def new_from_inbox_task(
        score_log_ref_id: EntityId,
        inbox_task: InboxTask,
        source: EventSource,
        created_time: Timestamp,
    ) -> "ScoreLogEntry":
        """Create an entry from an inbox task."""
        if not inbox_task.status.is_completed:
            raise Exception(
                "Cannot create score logs for inbox tasks that are not complete!"
            )

        has_lucky_puppy_bonus = None
        if inbox_task.status == InboxTaskStatus.DONE:
            has_lucky_puppy_bonus = random.randint(0, 99) < 10

        score_log_entry = ScoreLogEntry(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                ScoreLogEntry.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=EntityName(f"For InboxTask #{inbox_task.ref_id} '{inbox_task.name}'"),
            score_log_ref_id=score_log_ref_id,
            source=ScoreSource.INBOX_TASK,
            task_ref_id=inbox_task.ref_id,
            difficulty=inbox_task.difficulty,
            success=inbox_task.status == InboxTaskStatus.DONE,
            has_lucky_puppy_bonus=has_lucky_puppy_bonus,
            score=ScoreLogEntry._compute_score_for_inbox_task(
                inbox_task, has_lucky_puppy_bonus
            ),
        )
        return score_log_entry

    @staticmethod
    def new_from_big_plan(
        score_log_ref_id: EntityId,
        big_plan: BigPlan,
        source: EventSource,
        created_time: Timestamp,
    ) -> "ScoreLogEntry":
        """Create an entry from an inbox task."""
        if not big_plan.status.is_completed:
            raise Exception(
                "Cannot create score logs for big plans that are not completed!e"
            )

        score_log_entry = ScoreLogEntry(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                ScoreLogEntry.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=EntityName(f"For BigPlan #{big_plan.ref_id} '{big_plan.name}'"),
            score_log_ref_id=score_log_ref_id,
            source=ScoreSource.BIG_PLAN,
            task_ref_id=big_plan.ref_id,
            difficulty=None,
            success=big_plan.status == BigPlanStatus.DONE,
            has_lucky_puppy_bonus=None,
            score=ScoreLogEntry._compute_score_for_big_plan(big_plan),
        )
        return score_log_entry

    @staticmethod
    def _compute_score_for_inbox_task(
        inbox_task: InboxTask, has_lucky_puppy_bonus: bool | None
    ) -> int:
        lucky_puppy_modifier = 1 if has_lucky_puppy_bonus else 0
        if inbox_task.status == InboxTaskStatus.DONE:
            if inbox_task.difficulty is None:
                return 1 + lucky_puppy_modifier
            elif inbox_task.difficulty == Difficulty.EASY:
                return 1 + lucky_puppy_modifier
            elif inbox_task.difficulty == Difficulty.MEDIUM:
                return 2 + lucky_puppy_modifier
            else:  # inbox_task.difficulty == Difficulty.HARD:
                return 5 + lucky_puppy_modifier
        else:  # inbox_task.status == InboxTaskStatus.NOT_DONE:
            if inbox_task.difficulty is None:
                return -1
            elif inbox_task.difficulty == Difficulty.EASY:
                return -1
            elif inbox_task.difficulty == Difficulty.MEDIUM:
                return -2
            else:  # inbox_task.difficulty == Difficulty.HARD:
                return -5

    @staticmethod
    def _compute_score_for_big_plan(big_plan: BigPlan) -> int:
        if big_plan.status == BigPlanStatus.DONE:
            return 10
        else:  # big_plan.status == BigPlanStatus.NOT_DONE:
            return -10
