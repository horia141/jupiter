"""Tests about chores."""

import pytest
from jupiter_webapi_client.api.chores.chore_create import (
    sync_detailed as chore_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.chore import Chore
from jupiter_webapi_client.models.chore_create_args import ChoreCreateArgs
from jupiter_webapi_client.models.difficulty import Difficulty
from jupiter_webapi_client.models.eisen import Eisen
from jupiter_webapi_client.models.recurring_task_period import RecurringTaskPeriod
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_chores_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.CHORES, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.CHORES, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_chore(logged_in_client: AuthenticatedClient):
    def _create_chore(
        name: str,
        period: RecurringTaskPeriod = RecurringTaskPeriod.WEEKLY,
        is_key: bool = False,
        eisen: Eisen = Eisen.REGULAR,
        difficulty: Difficulty = Difficulty.MEDIUM,
        must_do: bool = False,
    ) -> Chore:
        result = chore_create_sync(
            client=logged_in_client,
            body=ChoreCreateArgs(
                name=name,
                period=period,
                is_key=is_key,
                eisen=eisen,
                difficulty=difficulty,
                must_do=must_do,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_chore

    return _create_chore


def test_chore_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/chores")

    expect(page.locator("#trunk-panel")).to_contain_text("There are no chores to show")


def test_chore_view_all(page: Page, create_chore) -> None:
    chore1 = create_chore(
        "Chore 1",
        RecurringTaskPeriod.WEEKLY,
        False,
        Eisen.REGULAR,
        Difficulty.MEDIUM,
        False,
    )
    chore2 = create_chore(
        "Chore 2",
        RecurringTaskPeriod.DAILY,
        True,
        Eisen.IMPORTANT,
        Difficulty.HARD,
        True,
    )
    chore3 = create_chore(
        "Chore 3",
        RecurringTaskPeriod.MONTHLY,
        False,
        Eisen.URGENT,
        Difficulty.EASY,
        False,
    )

    page.goto("/app/workspace/chores")

    expect(page.locator(f"#chore-{chore1.ref_id}")).to_contain_text("Chore 1")
    expect(page.locator(f"#chore-{chore2.ref_id}")).to_contain_text("Chore 2")
    expect(page.locator(f"#chore-{chore3.ref_id}")).to_contain_text("Chore 3")
