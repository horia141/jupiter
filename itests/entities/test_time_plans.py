"""Tests about time plans."""

import datetime
import re
import time
from collections.abc import Iterator

import pytest
from jupiter_webapi_client.api.big_plans.big_plan_create import (
    sync_detailed as big_plan_create_sync,
)
from jupiter_webapi_client.api.big_plans.big_plan_update import (
    sync_detailed as big_plan_update_sync,
)
from jupiter_webapi_client.api.inbox_tasks.inbox_task_create import (
    sync_detailed as inbox_task_create_sync,
)
from jupiter_webapi_client.api.inbox_tasks.inbox_task_update import (
    sync_detailed as inbox_task_update_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.api.time_plans.time_plan_associate_with_big_plans import (
    sync_detailed as time_plan_activity_create_big_plan_sync,
)
from jupiter_webapi_client.api.time_plans.time_plan_associate_with_inbox_tasks import (
    sync_detailed as time_plan_activity_create_inbox_task_sync,
)
from jupiter_webapi_client.api.time_plans.time_plan_create import (
    sync_detailed as time_plan_create_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.big_plan import BigPlan
from jupiter_webapi_client.models.big_plan_create_args import BigPlanCreateArgs
from jupiter_webapi_client.models.big_plan_status import BigPlanStatus
from jupiter_webapi_client.models.big_plan_update_args import BigPlanUpdateArgs
from jupiter_webapi_client.models.big_plan_update_args_actionable_date import (
    BigPlanUpdateArgsActionableDate,
)
from jupiter_webapi_client.models.big_plan_update_args_due_date import (
    BigPlanUpdateArgsDueDate,
)
from jupiter_webapi_client.models.big_plan_update_args_name import BigPlanUpdateArgsName
from jupiter_webapi_client.models.big_plan_update_args_project_ref_id import (
    BigPlanUpdateArgsProjectRefId,
)
from jupiter_webapi_client.models.big_plan_update_args_status import (
    BigPlanUpdateArgsStatus,
)
from jupiter_webapi_client.models.difficulty import Difficulty
from jupiter_webapi_client.models.eisen import Eisen
from jupiter_webapi_client.models.inbox_task import InboxTask
from jupiter_webapi_client.models.inbox_task_create_args import InboxTaskCreateArgs
from jupiter_webapi_client.models.inbox_task_status import InboxTaskStatus
from jupiter_webapi_client.models.inbox_task_update_args import InboxTaskUpdateArgs
from jupiter_webapi_client.models.inbox_task_update_args_actionable_date import (
    InboxTaskUpdateArgsActionableDate,
)
from jupiter_webapi_client.models.inbox_task_update_args_big_plan_ref_id import (
    InboxTaskUpdateArgsBigPlanRefId,
)
from jupiter_webapi_client.models.inbox_task_update_args_difficulty import (
    InboxTaskUpdateArgsDifficulty,
)
from jupiter_webapi_client.models.inbox_task_update_args_due_date import (
    InboxTaskUpdateArgsDueDate,
)
from jupiter_webapi_client.models.inbox_task_update_args_eisen import (
    InboxTaskUpdateArgsEisen,
)
from jupiter_webapi_client.models.inbox_task_update_args_name import (
    InboxTaskUpdateArgsName,
)
from jupiter_webapi_client.models.inbox_task_update_args_project_ref_id import (
    InboxTaskUpdateArgsProjectRefId,
)
from jupiter_webapi_client.models.inbox_task_update_args_status import (
    InboxTaskUpdateArgsStatus,
)
from jupiter_webapi_client.models.recurring_task_period import RecurringTaskPeriod
from jupiter_webapi_client.models.time_plan import TimePlan
from jupiter_webapi_client.models.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter_webapi_client.models.time_plan_activity_kind import TimePlanActivityKind
from jupiter_webapi_client.models.time_plan_associate_with_big_plans_args import (
    TimePlanAssociateWithBigPlansArgs,
)
from jupiter_webapi_client.models.time_plan_associate_with_inbox_tasks_args import (
    TimePlanAssociateWithInboxTasksArgs,
)
from jupiter_webapi_client.models.time_plan_create_args import TimePlanCreateArgs
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from jupiter_webapi_client.types import UNSET
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_time_plans_feature(logged_in_client: AuthenticatedClient) -> Iterator[None]:
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.TIME_PLANS, value=True),
    )
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.BIG_PLANS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.BIG_PLANS, value=False),
    )
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.TIME_PLANS, value=False),
    )


@pytest.fixture()
def create_time_plan(logged_in_client: AuthenticatedClient):
    def _create_time_plan(day: str, period: RecurringTaskPeriod) -> TimePlan:
        result = time_plan_create_sync(
            client=logged_in_client,
            body=TimePlanCreateArgs(today=day, period=period),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_time_plan

    return _create_time_plan


@pytest.fixture()
def create_time_plan_activity_from_big_plan(logged_in_client: AuthenticatedClient):
    def _create_time_plan_activity(time_plan_id: int, big_plan_id: int) -> None:
        result = time_plan_activity_create_big_plan_sync(
            client=logged_in_client,
            body=TimePlanAssociateWithBigPlansArgs(
                ref_id=time_plan_id,
                big_plan_ref_ids=[big_plan_id],
                override_existing_dates=False,
                kind=TimePlanActivityKind.FINISH,
                feasability=TimePlanActivityFeasability.MUST_DO,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_time_plan_activities[0]

    return _create_time_plan_activity


@pytest.fixture()
def create_time_plan_activity_from_inbox_task(logged_in_client: AuthenticatedClient):
    def _create_time_plan_activity(time_plan_id: int, inbox_task_id: int) -> None:
        result = time_plan_activity_create_inbox_task_sync(
            client=logged_in_client,
            body=TimePlanAssociateWithInboxTasksArgs(
                ref_id=time_plan_id,
                inbox_task_ref_ids=[inbox_task_id],
                override_existing_dates=False,
                kind=TimePlanActivityKind.FINISH,
                feasability=TimePlanActivityFeasability.MUST_DO,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_time_plan_activities[0]

    return _create_time_plan_activity


@pytest.fixture()
def create_inbox_task(logged_in_client: AuthenticatedClient):
    def _create_inbox_task(
        name: str, big_plan_id: int | None = None, due_date: str | None = None
    ) -> InboxTask:
        result = inbox_task_create_sync(
            client=logged_in_client,
            body=InboxTaskCreateArgs(
                name=name,
                is_key=False,
                big_plan_ref_id=big_plan_id or UNSET,
                due_date=due_date or UNSET,
                eisen=Eisen.REGULAR,
                difficulty=Difficulty.EASY,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_inbox_task

    return _create_inbox_task


@pytest.fixture()
def create_big_plan(logged_in_client: AuthenticatedClient):
    def _create_big_plan(
        name: str, actionable_date: str | None = None, due_date: str | None = None
    ) -> BigPlan:
        result = big_plan_create_sync(
            client=logged_in_client,
            body=BigPlanCreateArgs(
                name=name,
                is_key=False,
                eisen=Eisen.REGULAR,
                difficulty=Difficulty.EASY,
                actionable_date=actionable_date or UNSET,
                due_date=due_date or UNSET,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_big_plan

    return _create_big_plan


def test_time_plan_view_all(page: Page, create_time_plan) -> None:
    time_plan1 = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    time_plan2 = create_time_plan("2024-06-19", RecurringTaskPeriod.DAILY)
    time_plan3 = create_time_plan("2024-06-19", RecurringTaskPeriod.WEEKLY)

    page.goto("/app/workspace/time-plans")

    expect(page.locator(f"#time-plan-{time_plan1.ref_id}")).to_contain_text(
        "Daily plan for 2024-06-18"
    )
    expect(page.locator(f"#time-plan-{time_plan2.ref_id}")).to_contain_text(
        "Daily plan for 2024-06-19"
    )
    expect(page.locator(f"#time-plan-{time_plan3.ref_id}")).to_contain_text(
        "Weekly plan for 2024-06-19"
    )


def test_time_plan_view_one(page: Page, create_time_plan) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator('input[name="rightNow"]')).to_have_value("2024-06-18")
    expect(page.locator('input[name="period"]')).to_have_value("daily")


def test_time_plan_create(page: Page, create_time_plan) -> None:
    page.goto("/app/workspace/time-plans/new")
    page.wait_for_selector("#leaf-panel")

    page.locator('input[name="rightNow"]').fill("2024-06-18")
    page.locator('button[id="period-weekly"]').click()
    page.locator("#time-plan-create").click()

    page.wait_for_url(re.compile(r"/app/workspace/time-plans/\d+"))

    page.wait_for_selector("#branch-panel")
    expect(page.locator('input[name="rightNow"]')).to_have_value("2024-06-18")
    expect(page.locator('button[aria-pressed="true"]')).to_have_text("Weekly")


def test_time_plan_update(page: Page, create_time_plan) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    page.locator('input[name="rightNow"]').fill("2024-06-19")
    page.locator('button[id="period-daily"]').click()
    page.locator("#time-plan-change-time-config").click()

    page.wait_for_url(re.compile(r"/app/workspace/time-plans/\d+"))

    page.wait_for_selector("#branch-panel")
    expect(page.locator('input[name="rightNow"]')).to_have_value("2024-06-19")
    expect(page.locator("button[id='period-daily']")).to_have_attribute(
        "aria-pressed", "true"
    )


def test_time_plan_change_note(page: Page, create_time_plan) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    page.wait_for_selector("#entity-block-editor")

    page.locator('#editorjs div[contenteditable="true"]').first.fill("This is a note.")

    page.wait_for_url(re.compile(r"/app/workspace/time-plans/\d+"))

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )
    time.sleep(1)  # Wait for the update to be saved.

    page.reload()

    page.wait_for_selector("#branch-panel")

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )


def test_time_plan_archive(page: Page, create_time_plan) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    page.locator("#branch-entity-archive").click()
    page.locator("#branch-entity-archive-confirm").click()

    expect(page.locator("#time-plan-change-time-config")).to_be_disabled()

    entity_id = page.url.split("/")[-1]
    expect(page.locator(f"#time-plan-{entity_id}")).to_have_count(0)


def test_time_plan_link_untracked_inbox_tasks(
    logged_in_client: AuthenticatedClient,
    page: Page,
    create_time_plan,
    create_inbox_task,
) -> None:
    time_plan = create_time_plan("2025-06-18", RecurringTaskPeriod.YEARLY)
    inbox_task = create_inbox_task("Untracked Inbox Task")
    _mark_inbox_task_done(logged_in_client, inbox_task)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator("#time-plan-untracked-inbox-tasks")).to_contain_text(
        "Untracked Inbox Task"
    )


def test_time_plan_link_untracked_big_plans(
    logged_in_client: AuthenticatedClient, page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2025-06-18", RecurringTaskPeriod.YEARLY)
    big_plan = create_big_plan("Untracked Big Plan")
    _mark_big_plan_done(logged_in_client, big_plan)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator("#time-plan-untracked-big-plans")).to_contain_text(
        "Untracked Big Plan"
    )


def test_time_plan_link_lower_time_plans(page: Page, create_time_plan) -> None:
    _ = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    _ = create_time_plan("2024-06-19", RecurringTaskPeriod.DAILY)
    time_plan2 = create_time_plan("2024-06-19", RecurringTaskPeriod.WEEKLY)

    page.goto(f"/app/workspace/time-plans/{time_plan2.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator("#time-plan-lower")).to_contain_text(
        "Daily plan for 2024-06-18"
    )
    expect(page.locator("#time-plan-lower")).to_contain_text(
        "Daily plan for 2024-06-19"
    )


def test_time_plan_link_higher_time_plan(page: Page, create_time_plan) -> None:
    time_plan1 = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    _ = create_time_plan("2024-06-19", RecurringTaskPeriod.DAILY)
    _ = create_time_plan("2024-06-19", RecurringTaskPeriod.WEEKLY)

    page.goto(f"/app/workspace/time-plans/{time_plan1.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator("#time-plan-higher")).to_contain_text(
        "Weekly plan for 2024-06-19"
    )


def test_time_plan_link_previous_time_plan(page: Page, create_time_plan) -> None:
    _ = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    time_plan1 = create_time_plan("2024-06-19", RecurringTaskPeriod.DAILY)
    _ = create_time_plan("2024-06-19", RecurringTaskPeriod.WEEKLY)

    page.goto(f"/app/workspace/time-plans/{time_plan1.ref_id}")
    page.wait_for_selector("#branch-panel")

    expect(page.locator("#time-plan-previous")).to_contain_text(
        "Daily plan for 2024-06-18"
    )


def test_time_plan_create_new_inbox_task_activity(page: Page, create_time_plan) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("a", has_text="New Inbox Task").click()

    page.wait_for_url(re.compile("/app/workspace/inbox-tasks/new"))

    page.locator('input[name="name"]').fill("New Inbox Task")
    page.locator("#inbox-task-create").click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(
        page.locator("button[id='time-plan-activity-kind-finish']")
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator("button[id='time-plan-activity-feasability-nice-to-have']")
    ).to_have_attribute("aria-pressed", "true")

    expect(page.locator("input[name='targetInboxTaskName']")).to_have_value(
        "New Inbox Task"
    )


def test_time_plan_create_new_inbox_task_with_big_plan_activity(
    page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    _ = create_big_plan("The Big Plan")
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("a", has_text="New Inbox Task").click()

    page.wait_for_url(re.compile("/app/workspace/inbox-tasks/new"))

    page.locator('input[name="name"]').fill("New Inbox Task")
    page.locator("#bigPlan").locator("..").click()
    page.locator("li", has_text="The Big Plan").click()

    page.locator("#inbox-task-create").click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(
        page.locator("button[id='time-plan-activity-kind-finish']")
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator("button[id='time-plan-activity-feasability-nice-to-have']")
    ).to_have_attribute("aria-pressed", "true")

    expect(page.locator("input[name='targetInboxTaskName']")).to_have_value(
        "New Inbox Task"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("New Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.locator("#time-plan-activities").locator("a", has_text="The Big Plan").click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(
        page.locator("button[id='time-plan-activity-kind-finish']")
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator("button[id='time-plan-activity-feasability-nice-to-have']")
    ).to_have_attribute("aria-pressed", "true")


def test_time_plan_create_new_big_plan_activity(
    page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="New Big Plan").click()

    page.wait_for_url(re.compile("/app/workspace/big-plans/new"))

    page.locator('input[name="name"]').fill("New Big Plan")
    page.locator("#big-plan-create").click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(
        page.locator("button[id='time-plan-activity-kind-finish']")
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator("button[id='time-plan-activity-feasability-nice-to-have']")
    ).to_have_attribute("aria-pressed", "true")

    expect(page.locator("#target")).to_contain_text("New Big Plan")


def test_time_plan_create_new_inbox_task_from_big_plan_activity(
    page: Page,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    big_plan = create_big_plan("The Big Plan")
    big_plan_activity = create_time_plan_activity_from_big_plan(
        time_plan.ref_id, big_plan.ref_id
    )

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{big_plan_activity.ref_id}"
    )

    page.locator("#leaf-panel").locator("a", has_text="New Inbox Task").click()

    page.wait_for_url(re.compile(r"/app/workspace/inbox-tasks/new"))

    page.locator('input[name="name"]').fill("The New Inbox Task")
    page.locator("#inbox-task-create").click()

    expect(page.locator("input[id='bigPlan']")).to_have_value("The Big Plan")

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The New Inbox Task")

    page.locator("#time-plan-activities").locator(
        "a", has_text="The New Inbox Task"
    ).click(force=True)

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    expect(
        page.locator("button[id='time-plan-activity-kind-finish']")
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator("button[id='time-plan-activity-feasability-must-do']")
    ).to_have_attribute("aria-pressed", "true")


def test_time_plan_create_activities_from_inbox_tasks_of_an_associated_big_plan(
    page: Page,
    create_time_plan,
    create_big_plan,
    create_inbox_task,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    big_plan = create_big_plan("The Big Plan")
    _ = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)
    _ = create_inbox_task("Other Inbox Task", big_plan_id=big_plan.ref_id)
    big_plan_activity = create_time_plan_activity_from_big_plan(
        time_plan.ref_id, big_plan.ref_id
    )

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{big_plan_activity.ref_id}"
    )

    page.locator("#leaf-panel").locator(
        "a", has_text="From Current Inbox Tasks"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"workspace/time-plans/{time_plan.ref_id}/add-from-current-inbox-tasks"
        )
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}/\d+"))

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "Other Inbox Task"
    )


def test_time_plan_associate_with_inbox_task(
    page: Page, create_time_plan, create_inbox_task
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-18")


def test_time_plan_associate_with_inbox_task_no_dates(
    page: Page, create_time_plan, create_inbox_task
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_associate_with_inbox_task_and_override_dates(
    page: Page, create_time_plan, create_inbox_task
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_associate_with_inbox_task_and_pulls_big_plan(
    page: Page, create_time_plan, create_inbox_task, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_with_inbox_task_and_pulls_big_plan_no_dates(
    page: Page, create_time_plan, create_inbox_task, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    _ = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_associate_with_inbox_task_and_pulls_big_plan_but_overwrites_dates_leave_alone(
    page: Page, create_time_plan, create_inbox_task, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_with_two_out_of_three_inbox_tasks(
    page: Page, create_time_plan, create_inbox_task
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    _ = create_inbox_task("The Inbox Task 1", due_date="2024-06-18")
    _ = create_inbox_task("The Inbox Task 2", due_date="2024-06-18")
    _ = create_inbox_task("The Inbox Task 3", due_date="2024-06-19")

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task 1"
    ).click()
    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task 2"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 2")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "The Inbox Task 3"
    )


def test_time_plan_associate_with_tasks_that_pull_in_some_more_big_plans(
    page: Page, create_time_plan, create_inbox_task, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan1 = create_big_plan(
        "The Big Plan 1", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_inbox_task("The Inbox Task 1", big_plan_id=big_plan1.ref_id)
    _ = create_inbox_task("The Inbox Task 2", big_plan_id=big_plan1.ref_id)
    big_plan2 = create_big_plan(
        "The Big Plan 2", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_inbox_task("The Inbox Task 3", big_plan_id=big_plan2.ref_id)
    _ = create_big_plan(
        "The Big Plan 3", actionable_date="2024-06-10", due_date="2024-06-19"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Inbox Tasks").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-inbox-tasks")
    )

    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task 1"
    ).click()
    page.locator("#time-plan-current-inbox-tasks").locator(
        "p", has_text="The Inbox Task 3"
    ).click()

    page.locator("#time-plan-current-inbox-tasks").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "The Inbox Task 2"
    )
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 3")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 2")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan 3")


def test_time_plan_associate_with_big_plan(
    page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Big Plans").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-big-plans")
    )

    page.locator("#time-plan-current-big-plans").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-big-plans").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_with_big_plan_no_dates(
    page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Big Plans").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-big-plans")
    )

    page.locator("#time-plan-current-big-plans").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-big-plans").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_associate_with_big_plan_and_override_dates(
    page: Page, create_time_plan, create_big_plan
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Current Big Plans").click()

    page.wait_for_url(
        re.compile(r"/app/workspace/time-plans/\d+/add-from-current-big-plans")
    )

    page.locator("#time-plan-current-big-plans").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-big-plans").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_associate_previous_activity_inbox_task(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-18")


def test_time_plan_associate_previous_activity_inbox_task_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)
    _clear_inbox_task_dates(logged_in_client, inbox_task)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-30")


def test_time_plan_associate_previous_activity_inbox_task_override_dates(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-30")


def test_time_plan_associate_previous_activity_inbox_task_and_pulls_big_plan(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_previous_activity_inbox_task_and_pulls_big_plan_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)
    _clear_big_plan_dates(logged_in_client, big_plan)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-24")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-30")


def test_time_plan_associate_previous_activity_inbox_task_and_pulls_big_plan_but_overwrites_dates_leave_alone(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_previous_activity_two_of_three_inbox_tasks(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task1 = create_inbox_task("The Inbox Task 1", due_date="2024-06-18")
    inbox_task2 = create_inbox_task("The Inbox Task 2", due_date="2024-06-18")
    inbox_task3 = create_inbox_task("The Inbox Task 3", due_date="2024-06-19")
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task1.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task2.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task3.ref_id
    )

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 1"
    ).click()
    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 3"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "The Inbox Task 2"
    )
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 3")


def test_time_plan_associate_previous_activity_tasks_that_pull_in_some_more_big_plans(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan1 = create_big_plan(
        "The Big Plan 1", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task1 = create_inbox_task("The Inbox Task 1", big_plan_id=big_plan1.ref_id)
    inbox_task2 = create_inbox_task("The Inbox Task 2", big_plan_id=big_plan1.ref_id)
    big_plan2 = create_big_plan(
        "The Big Plan 2", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task3 = create_inbox_task("The Inbox Task 3", big_plan_id=big_plan2.ref_id)
    big_plan3 = create_big_plan(
        "The Big Plan 3", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task1.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task2.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task3.ref_id
    )
    _ = create_time_plan_activity_from_big_plan(time_plan_1.ref_id, big_plan3.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 1"
    ).click()
    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 3"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "The Inbox Task 2"
    )
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 3")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 2")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan 3")


def test_time_plan_associate_previous_activity_big_plan(
    page: Page,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_time_plan_activity_from_big_plan(time_plan_1.ref_id, big_plan.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_associate_previous_activity_big_plan_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    _ = create_time_plan_activity_from_big_plan(time_plan_1.ref_id, big_plan.ref_id)
    _clear_big_plan_dates(logged_in_client, big_plan)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-24")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-30")


def test_time_plan_associate_previous_activity_big_plan_and_override_dates(
    page: Page,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    _ = create_time_plan_activity_from_big_plan(time_plan_1.ref_id, big_plan.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Big Plan"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add And Override Dates$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-24")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-30")


def test_time_plan_associate_previous_activity_some_already_associated(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task1 = create_inbox_task("The Inbox Task 1", due_date="2024-06-18")
    inbox_task2 = create_inbox_task("The Inbox Task 2", due_date="2024-06-18")
    inbox_task3 = create_inbox_task("The Inbox Task 3", due_date="2024-06-19")
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task1.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task2.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_1.ref_id, inbox_task3.ref_id
    )
    _ = create_time_plan_activity_from_inbox_task(
        time_plan_2.ref_id, inbox_task2.ref_id
    )

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    page.locator("#section-action-nav-multiple-compact-button").click()
    page.locator("a", has_text="From Time Plans").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_2.ref_id}"
        )
    )

    page.locator("#time-plan-previous-time-plan").locator(
        "a", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/{time_plan_2.ref_id}/add-from-current-time-plans/{time_plan_1.ref_id}"
        )
    )

    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 1"
    ).click()
    page.locator("#time-plan-current-activities").locator(
        "p", has_text="The Inbox Task 3"
    ).click()

    page.locator("#time-plan-current-activities").locator(
        "button", has_text=re.compile(r"^Add$")
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/time-plans/{time_plan_2.ref_id}"))

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 2")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 3")


def test_time_plan_add_an_inbox_task_to_a_big_plan_updates_all_time_plans(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan_1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan_2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task = create_inbox_task("The Inbox Task")
    _ = create_time_plan_activity_from_inbox_task(time_plan_1.ref_id, inbox_task.ref_id)
    _ = create_time_plan_activity_from_inbox_task(time_plan_2.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan_1.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan")

    _associate_inbox_task_with_big_plan(logged_in_client, inbox_task, big_plan)

    page.goto(f"/app/workspace/time-plans/{time_plan_1.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/time-plans/{time_plan_2.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_with_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    inbox_task = create_inbox_task("The Inbox Task", due_date="2024-06-18")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Daily plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Daily plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-18")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_and_pulls_big_plan(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_and_pulls_big_plan_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_and_pulls_big_plan_but_overwrites_dates_leave_alone(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator(
        "button", has_text="Add And Override Dates"
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_add_an_inbox_task_to_multiple_already_existing_time_plans(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")

    page.goto(f"/app/workspace/inbox-tasks/{inbox_task.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()
    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-25"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task.ref_id}"))

    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )
    expect(page.locator("#inbox-task-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-25"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan1.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(f"/app/workspace/time-plans/{time_plan2.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")


def test_time_plan_add_an_inbox_task_to_an_already_existing_time_plan_with_tasks_that_pull_in_some_more_big_plans(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan1 = create_big_plan(
        "The Big Plan 1", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task1 = create_inbox_task("The Inbox Task 1", big_plan_id=big_plan1.ref_id)
    create_inbox_task("The Inbox Task 2", big_plan_id=big_plan1.ref_id)
    big_plan2 = create_big_plan(
        "The Big Plan 2", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    inbox_task3 = create_inbox_task("The Inbox Task 3", big_plan_id=big_plan2.ref_id)
    create_big_plan(
        "The Big Plan 3", actionable_date="2024-06-10", due_date="2024-06-19"
    )

    # Add first inbox task
    page.goto(f"/app/workspace/inbox-tasks/{inbox_task1.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task1.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task1.ref_id}"))

    # Add third inbox task
    page.goto(f"/app/workspace/inbox-tasks/{inbox_task3.ref_id}")

    page.locator("#inbox-task-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-inbox-task-to-plans\?inboxTaskRefId={inbox_task3.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-inbox-task-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/inbox-tasks/{inbox_task3.ref_id}"))

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).not_to_contain_text(
        "The Inbox Task 2"
    )
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 3")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan 2")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan 3")


def test_time_plan_show_activity_doneness(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")
    _ = create_time_plan_activity_from_inbox_task(time_plan.ref_id, inbox_task.ref_id)

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(
        page.locator("#time-plan-activities").locator("p", has_text="The Inbox Task")
    ).not_to_have_css("font-weight", "100")

    _mark_inbox_task_done(logged_in_client, inbox_task)
    page.reload()

    expect(
        page.locator("#time-plan-activities").locator("p", has_text="The Inbox Task")
    ).to_have_css("font-weight", "700")


def test_time_plan_activity_update(
    page: Page,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")
    inbox_task_activity = create_time_plan_activity_from_inbox_task(
        time_plan.ref_id, inbox_task.ref_id
    )

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{inbox_task_activity.ref_id}"
    )

    page.locator("#time-plan-activity-kind-make-progress").click()
    page.locator("#time-plan-activity-feasability-stretch").click()
    page.locator("#time-plan-activity-properties").locator(
        "button", has_text="Save"
    ).click()

    page.reload()

    expect(
        page.locator('button[id="time-plan-activity-kind-finish"]')
    ).to_have_attribute("aria-pressed", "false")
    expect(
        page.locator('button[id="time-plan-activity-kind-make-progress"]')
    ).to_have_attribute("aria-pressed", "true")
    expect(
        page.locator('button[id="time-plan-activity-feasability-must-do"]')
    ).to_have_attribute("aria-pressed", "false")
    expect(
        page.locator('button[id="time-plan-activity-feasability-nice-to-have"]')
    ).to_have_attribute("aria-pressed", "false")
    expect(
        page.locator('button[id="time-plan-activity-feasability-stretch"]')
    ).to_have_attribute("aria-pressed", "true")


def test_time_plan_activity_archive_inbox_task(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_time_plan_activity_from_inbox_task,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    inbox_task = create_inbox_task("The Inbox Task")
    inbox_task_activity = create_time_plan_activity_from_inbox_task(
        time_plan.ref_id, inbox_task.ref_id
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{inbox_task_activity.ref_id}"
    )

    page.locator("#leaf-entity-archive").click()
    page.locator("#leaf-entity-archive-confirm").click()

    expect(page.locator("#leaf-entity-archive")).to_be_disabled()

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Inbox Task")


def test_time_plan_activity_archive_big_plan_with_inbox_task(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_inbox_task,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    inbox_task = create_inbox_task("The Inbox Task", big_plan_id=big_plan.ref_id)
    big_plan_activity = create_time_plan_activity_from_big_plan(
        time_plan.ref_id, big_plan.ref_id
    )
    inbox_task_activity = create_time_plan_activity_from_inbox_task(
        time_plan.ref_id, inbox_task.ref_id
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{big_plan_activity.ref_id}"
    )

    page.locator("#leaf-entity-archive").click()
    page.locator("#leaf-entity-archive-confirm").click()

    page.goto(
        f"/app/workspace/time-plans/{time_plan.ref_id}/{inbox_task_activity.ref_id}"
    )

    expect(page.locator("#inbox-task-editor-save")).to_be_disabled()

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")

    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Inbox Task")
    expect(page.locator("#time-plan-activities")).not_to_contain_text("The Big Plan")


def test_time_plan_periods_settings_standard(page: Page) -> None:
    page.goto("/app/workspace/time-plans")

    expect(page.locator("a", has_text="Create a quarterly time plan")).to_be_attached()
    expect(page.locator("a", has_text="Create a weekly time plan")).to_be_attached()


def test_time_plan_periods_settings_add_monthly(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Monthly").click()
    page.locator("button", has_text="None").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("a", has_text="Create a monthly time plan")).to_be_attached()
    expect(page.locator("a", has_text="Create a quarterly time plan")).to_be_attached()
    expect(page.locator("a", has_text="Create a weekly time plan")).to_be_attached()


def test_time_plan_generate_standard_config_via_gen(page: Page, new_user) -> None:
    page.goto("/app/workspace/tools/gen")

    page.locator("#generate").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_standard_config_via_save(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_different_config_add_monthly(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Monthly").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Monthly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).to_contain_text("Make monthly plan for")
    expect(page.locator("html")).to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_different_config_remove_quarterly(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Quarterly").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).not_to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).to_contain_text("Make weekly plan for")
    expect(page.locator("html")).not_to_contain_text("Make quarterly plan for")


def test_time_plan_generate_no_planning_tasks(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Only Plan").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).not_to_contain_text("Make weekly plan for")
    expect(page.locator("html")).not_to_contain_text("Make quarterly plan for")


def test_time_plan_generate_no_nothing(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="None").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).not_to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).not_to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).not_to_contain_text("Make weekly plan for")
    expect(page.locator("html")).not_to_contain_text("Make quarterly plan for")


def test_time_plan_generate_no_nothing_and_regenerate(page: Page) -> None:
    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="None").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).not_to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).not_to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Both Plan And Task").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_does_not_override_existing_time_plans(
    page: Page, create_time_plan
) -> None:
    right_now = datetime.datetime.now(tz=datetime.timezone.utc)
    _ = create_time_plan(right_now.strftime("%Y-%m-%d"), RecurringTaskPeriod.WEEKLY)

    page.goto("/app/workspace/time-plans/settings")

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all", has_text="Weekly plan for")).to_contain_text(
        "User"
    )
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")
    expect(
        page.locator("#time-plans-all", has_text="Quarterly plan for")
    ).to_contain_text("Recurring")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).not_to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_does_not_override_existing_time_plans_with_no_periods(
    page: Page, create_time_plan
) -> None:
    right_now = datetime.datetime.now(tz=datetime.timezone.utc)
    _ = create_time_plan(right_now.strftime("%Y-%m-%d"), RecurringTaskPeriod.WEEKLY)

    page.goto("/app/workspace/time-plans/settings")

    page.locator("button", has_text="Weekly").click()

    page.locator("#time-plans-settings-save").click()

    page.goto("/app/workspace/time-plans")

    expect(page.locator("#time-plans-all")).to_contain_text("Weekly plan for")
    expect(page.locator("#time-plans-all", has_text="Weekly plan for")).to_contain_text(
        "User"
    )
    expect(page.locator("#time-plans-all")).to_contain_text("Quarterly plan for")
    expect(
        page.locator("#time-plans-all", has_text="Quarterly plan for")
    ).to_contain_text("Recurring")

    page.goto("/app/workspace/inbox-tasks")

    expect(page.locator("html")).not_to_contain_text("Make weekly plan for")
    expect(page.locator("html")).to_contain_text("Make quarterly plan for")


def test_time_plan_generate_time_plan_is_not_editable(page: Page) -> None:
    page.goto("/app/workspace/tools/gen")

    page.locator("#generate").click()

    page.goto("/app/workspace/time-plans")

    page.locator("#time-plans-all", has_text="Weekly plan for").click()

    expect(page.locator("input[name='rightNow']")).to_have_attribute("readonly", "")
    expect(page.locator('button[id="period-daily"]')).to_be_disabled()
    expect(page.locator('button[id="period-weekly"]')).to_be_disabled()
    expect(page.locator('button[id="period-monthly"]')).to_be_disabled()
    expect(page.locator('button[id="period-quarterly"]')).to_be_disabled()
    expect(page.locator('button[id="period-yearly"]')).to_be_disabled()
    expect(page.locator("#time-plan-change-time-config")).to_be_disabled()


def test_time_plan_generate_planning_task_links_to_time_plan(page: Page) -> None:
    page.goto("/app/workspace/tools/gen")

    page.locator("#generate").click()

    page.goto("/app/workspace/inbox-tasks")

    page.locator("html", has_text="Make weekly plan for").click()

    page.wait_for_url(re.compile(r"/app/workspace/inbox-tasks/\d+"))

    page.locator("#leaf-panel").locator("a", has_text="Time Plan").click()

    page.wait_for_url(re.compile(r"/app/workspace/time-plans/\d+"))

    expect(page.locator('button[aria-pressed="true"]')).to_have_text("Weekly")


def _mark_inbox_task_done(
    logged_in_client: AuthenticatedClient, inbox_task: InboxTask
) -> None:
    inbox_task_update_sync(
        client=logged_in_client,
        body=InboxTaskUpdateArgs(
            ref_id=inbox_task.ref_id,
            name=InboxTaskUpdateArgsName(should_change=False),
            status=InboxTaskUpdateArgsStatus(
                should_change=True, value=InboxTaskStatus.DONE
            ),
            eisen=InboxTaskUpdateArgsEisen(should_change=False),
            difficulty=InboxTaskUpdateArgsDifficulty(should_change=False),
            actionable_date=InboxTaskUpdateArgsActionableDate(should_change=False),
            due_date=InboxTaskUpdateArgsDueDate(should_change=False),
            project_ref_id=InboxTaskUpdateArgsProjectRefId(should_change=False),
            big_plan_ref_id=InboxTaskUpdateArgsBigPlanRefId(should_change=False),
        ),
    )


def _clear_inbox_task_dates(
    logged_in_client: AuthenticatedClient, inbox_task: InboxTask
) -> None:
    inbox_task_update_sync(
        client=logged_in_client,
        body=InboxTaskUpdateArgs(
            ref_id=inbox_task.ref_id,
            name=InboxTaskUpdateArgsName(should_change=False),
            status=InboxTaskUpdateArgsStatus(should_change=False),
            eisen=InboxTaskUpdateArgsEisen(should_change=False),
            difficulty=InboxTaskUpdateArgsDifficulty(should_change=False),
            actionable_date=InboxTaskUpdateArgsActionableDate(
                should_change=True, value=None
            ),
            due_date=InboxTaskUpdateArgsDueDate(should_change=True, value=None),
            project_ref_id=InboxTaskUpdateArgsProjectRefId(should_change=False),
            big_plan_ref_id=InboxTaskUpdateArgsBigPlanRefId(should_change=False),
        ),
    )


def _associate_inbox_task_with_big_plan(
    logged_in_client: AuthenticatedClient, inbox_task: InboxTask, big_plan: BigPlan
) -> None:
    inbox_task_update_sync(
        client=logged_in_client,
        body=InboxTaskUpdateArgs(
            ref_id=inbox_task.ref_id,
            name=InboxTaskUpdateArgsName(should_change=False),
            status=InboxTaskUpdateArgsStatus(should_change=False),
            eisen=InboxTaskUpdateArgsEisen(should_change=False),
            difficulty=InboxTaskUpdateArgsDifficulty(should_change=False),
            actionable_date=InboxTaskUpdateArgsActionableDate(should_change=False),
            due_date=InboxTaskUpdateArgsDueDate(should_change=False),
            project_ref_id=InboxTaskUpdateArgsProjectRefId(should_change=False),
            big_plan_ref_id=InboxTaskUpdateArgsBigPlanRefId(
                should_change=True, value=big_plan.ref_id
            ),
        ),
    )


def _mark_big_plan_done(
    logged_in_client: AuthenticatedClient, big_plan: BigPlan
) -> None:
    big_plan_update_sync(
        client=logged_in_client,
        body=BigPlanUpdateArgs(
            ref_id=big_plan.ref_id,
            name=BigPlanUpdateArgsName(should_change=False),
            status=BigPlanUpdateArgsStatus(
                should_change=True, value=BigPlanStatus.DONE
            ),
            actionable_date=BigPlanUpdateArgsActionableDate(should_change=False),
            due_date=BigPlanUpdateArgsDueDate(should_change=False),
            project_ref_id=BigPlanUpdateArgsProjectRefId(should_change=False),
        ),
    )


def _clear_big_plan_dates(
    logged_in_client: AuthenticatedClient, big_plan: BigPlan
) -> None:
    big_plan_update_sync(
        client=logged_in_client,
        body=BigPlanUpdateArgs(
            ref_id=big_plan.ref_id,
            name=BigPlanUpdateArgsName(should_change=False),
            status=BigPlanUpdateArgsStatus(should_change=False),
            actionable_date=BigPlanUpdateArgsActionableDate(
                should_change=True, value=None
            ),
            due_date=BigPlanUpdateArgsDueDate(should_change=True, value=None),
            project_ref_id=BigPlanUpdateArgsProjectRefId(should_change=False),
        ),
    )


def test_time_plan_add_big_plan_to_an_already_existing_time_plan(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_with_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.DAILY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-18", due_date="2024-06-18"
    )

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Daily plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Daily plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-18")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-18")


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_and_override_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator(
        "button", has_text="Add And Override Dates"
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_add_big_plan_to_multiple_already_existing_time_plans(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan1 = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    time_plan2 = create_time_plan("2024-06-25", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()
    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-25"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )
    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-25"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan1.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")

    page.goto(f"/app/workspace/time-plans/{time_plan2.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_with_inbox_tasks(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    create_inbox_task("The Inbox Task 1", big_plan_id=big_plan.ref_id)
    create_inbox_task("The Inbox Task 2", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 2")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_with_inbox_tasks_no_dates(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan("The Big Plan")
    create_inbox_task("The Inbox Task 1", big_plan_id=big_plan.ref_id)
    create_inbox_task("The Inbox Task 2", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator("button", has_text="Add").click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 2")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-17")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-23")


def test_time_plan_add_big_plan_to_an_already_existing_time_plan_with_inbox_tasks_but_overwrites_dates_leave_alone(
    page: Page,
    logged_in_client: AuthenticatedClient,
    create_time_plan,
    create_inbox_task,
    create_big_plan,
    create_time_plan_activity_from_big_plan,
) -> None:
    time_plan = create_time_plan("2024-06-18", RecurringTaskPeriod.WEEKLY)
    big_plan = create_big_plan(
        "The Big Plan", actionable_date="2024-06-10", due_date="2024-06-19"
    )
    create_inbox_task("The Inbox Task 1", big_plan_id=big_plan.ref_id)
    create_inbox_task("The Inbox Task 2", big_plan_id=big_plan.ref_id)

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")

    page.locator("#big-plan-time-plans").locator("a", has_text="Add").click()

    page.wait_for_url(
        re.compile(
            rf"/app/workspace/time-plans/add-big-plan-to-plans\?bigPlanRefId={big_plan.ref_id}"
        )
    )

    page.locator("#all-time-plans").locator(
        "p", has_text="Weekly plan for 2024-06-18"
    ).click()

    page.locator("#add-big-plan-to-plans").locator(
        "button", has_text="Add And Override Dates"
    ).click()

    page.wait_for_url(re.compile(rf"/app/workspace/big-plans/{big_plan.ref_id}"))

    expect(page.locator("#big-plan-time-plans").locator("p")).to_contain_text(
        "Weekly plan for 2024-06-18"
    )

    page.goto(f"/app/workspace/time-plans/{time_plan.ref_id}")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Big Plan")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 1")
    expect(page.locator("#time-plan-activities")).to_contain_text("The Inbox Task 2")

    page.goto(f"/app/workspace/big-plans/{big_plan.ref_id}")
    expect(page.locator("input[name='actionableDate']")).to_have_value("2024-06-10")
    expect(page.locator("input[name='dueDate']")).to_have_value("2024-06-19")


# ideas
# * view time plan should show some activities
# * test that created activities show up in the timeplan too
