"""Tests about big plans."""

import pytest
from jupiter_webapi_client.api.big_plans.big_plan_create import (
    sync_detailed as big_plan_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.big_plan import BigPlan
from jupiter_webapi_client.models.big_plan_create_args import BigPlanCreateArgs
from jupiter_webapi_client.models.difficulty import Difficulty
from jupiter_webapi_client.models.eisen import Eisen
from jupiter_webapi_client.models.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter_webapi_client.models.time_plan_activity_kind import TimePlanActivityKind
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_big_plans_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.BIG_PLANS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.BIG_PLANS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_big_plan(logged_in_client: AuthenticatedClient):
    def _create_big_plan(
        name: str,
        is_key: bool = False,
        eisen: Eisen = Eisen.REGULAR,
        difficulty: Difficulty = Difficulty.MEDIUM,
        actionable_date: str | None = None,
        due_date: str | None = None,
        time_plan_activity_kind: TimePlanActivityKind | None = None,
        time_plan_activity_feasability: TimePlanActivityFeasability | None = None,
    ) -> BigPlan:
        result = big_plan_create_sync(
            client=logged_in_client,
            body=BigPlanCreateArgs(
                name=name,
                is_key=is_key,
                eisen=eisen,
                difficulty=difficulty,
                actionable_date=actionable_date,
                due_date=due_date,
                time_plan_activity_kind=time_plan_activity_kind,
                time_plan_activity_feasability=time_plan_activity_feasability,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_big_plan

    return _create_big_plan


def test_big_plan_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/big-plans")

    expect(page.locator("#trunk-panel")).to_contain_text(
        "There are no big plans to show"
    )


def test_big_plan_view_all(page: Page, create_big_plan) -> None:
    big_plan1 = create_big_plan("Big Plan 1", False, Eisen.REGULAR, Difficulty.MEDIUM)
    big_plan2 = create_big_plan(
        "Big Plan 2", True, Eisen.IMPORTANT, Difficulty.HARD, "2024-01-01", "2024-12-31"
    )
    big_plan3 = create_big_plan(
        "Big Plan 3",
        False,
        Eisen.URGENT,
        Difficulty.EASY,
        None,
        "2024-06-30",
        TimePlanActivityKind.MAKE_PROGRESS,
        TimePlanActivityFeasability.MUST_DO,
    )

    page.goto("/app/workspace/big-plans")

    expect(page.locator(f"#big-plan-{big_plan1.ref_id}")).to_contain_text("Big Plan 1")
    expect(page.locator(f"#big-plan-{big_plan2.ref_id}")).to_contain_text("Big Plan 2")
    expect(page.locator(f"#big-plan-{big_plan3.ref_id}")).to_contain_text("Big Plan 3")
