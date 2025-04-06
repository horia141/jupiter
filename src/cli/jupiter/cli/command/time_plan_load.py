"""Command for loading the time plans."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    big_plan_status_to_rich_text,
    difficulty_to_rich_text,
    eisen_to_rich_text,
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    inbox_task_status_to_rich_text,
    period_to_rich_text,
    source_to_rich_text,
    time_plan_activity_feasability_to_rich_text,
    time_plan_activity_kind_to_rich_text,
    time_plan_source_to_rich_text,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.use_cases.concept.time_plans.load import (
    TimePlanLoadResult,
    TimePlanLoadUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class TimePlanLoad(LoggedInReadonlyCommand[TimePlanLoadUseCase, TimePlanLoadResult]):
    """Command for loading the time plans."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: TimePlanLoadResult,
    ) -> None:
        time_plan = result.time_plan
        inbox_tasks_by_ref_id = {t.ref_id: t for t in result.target_inbox_tasks or []}
        big_plans_by_ref_id = {t.ref_id: t for t in result.target_big_plans or []}
        sorted_activities = sorted(
            result.activities, key=lambda a: (a.archived, a.feasability, a.kind)
        )

        time_plan_text = (
            Text("🏭 ")
            .append(entity_id_to_rich_text(time_plan.ref_id))
            .append(" ")
            .append(entity_name_to_rich_text(time_plan.name))
            .append(" ")
            .append(time_plan_source_to_rich_text(time_plan.source))
            .append(" ")
            .append(period_to_rich_text(time_plan.period))
        )

        rich_tree = Tree(time_plan_text, guide_style="bold bright_blue")

        activity_tree = rich_tree.add("Activities")

        for activity in sorted_activities:
            if activity.target == TimePlanActivityTarget.INBOX_TASK:
                target_inbox_task = inbox_tasks_by_ref_id[activity.target_ref_id]
                target_name_text = entity_name_to_rich_text(target_inbox_task.name)
                target_status_text = inbox_task_status_to_rich_text(
                    target_inbox_task.status, target_inbox_task.archived
                )
            else:
                target_big_plan = big_plans_by_ref_id[activity.target_ref_id]
                target_name_text = entity_name_to_rich_text(target_big_plan.name)
                target_status_text = big_plan_status_to_rich_text(
                    target_big_plan.status, target_big_plan.archived
                )

            activity_text = (
                Text("")
                .append(entity_id_to_rich_text(activity.ref_id))
                .append(" Work on ")
                .append(
                    "inbox task "
                    if activity.target == TimePlanActivityTarget.INBOX_TASK
                    else "big plan "
                )
                .append(entity_id_to_rich_text(activity.target_ref_id))
                .append(" ")
                .append(target_name_text)
                .append(" [")
                .append(target_status_text)
                .append("] ")
                .append(time_plan_activity_kind_to_rich_text(activity.kind))
                .append(" ")
                .append(
                    time_plan_activity_feasability_to_rich_text(activity.feasability)
                )
            )

            activity_tree.add(activity_text)

        if (
            result.completed_nontarget_inbox_tasks is not None
            and len(result.completed_nontarget_inbox_tasks) > 0
        ):
            completed_nontarget_tree = rich_tree.add(
                "Completed Non-targets Inbox Tasks"
            )

            sorted_inbox_tasks = sorted(
                result.completed_nontarget_inbox_tasks,
                key=lambda it: (
                    it.archived,
                    it.eisen,
                    it.status,
                    it.due_date or ADate.from_str("2100-01-01"),
                    it.difficulty,
                ),
            )

            for inbox_task in sorted_inbox_tasks:
                inbox_task_text = inbox_task_status_to_rich_text(
                    inbox_task.status,
                    inbox_task.archived,
                )
                inbox_task_text.append(" ").append(
                    entity_id_to_rich_text(inbox_task.ref_id)
                ).append(f" {inbox_task.name}").append(" ").append(
                    source_to_rich_text(inbox_task.source)
                ).append(
                    " "
                ).append(
                    eisen_to_rich_text(inbox_task.eisen)
                )

                if inbox_task.difficulty:
                    inbox_task_text.append(" ").append(
                        difficulty_to_rich_text(inbox_task.difficulty),
                    )

                completed_nontarget_tree.add(inbox_task_text)

        if (
            result.completed_nottarget_big_plans
            and len(result.completed_nottarget_big_plans) > 0
        ):
            completed_nontarget_tree = rich_tree.add("Completed Non-targets Big Plans")

            sorted_big_plans = sorted(
                result.completed_nottarget_big_plans,
                key=lambda bpe: (
                    bpe.archived,
                    bpe.status,
                    (
                        bpe.actionable_date
                        if bpe.actionable_date
                        else ADate.from_str("2100-01-01")
                    ),
                ),
            )

            for big_plan in sorted_big_plans:
                big_plan_text = big_plan_status_to_rich_text(
                    big_plan.status,
                    big_plan.archived,
                )
                big_plan_text.append(" ").append(
                    entity_id_to_rich_text(big_plan.ref_id)
                ).append(f" {big_plan.name}")

                completed_nontarget_tree.add(big_plan_text)

        console.print(rich_tree)
