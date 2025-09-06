"""Tests about journals."""

import pendulum
import pytest
from jupiter_webapi_client.api.journals.journal_create import (
    sync_detailed as journal_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.journal import Journal
from jupiter_webapi_client.models.journal_create_args import JournalCreateArgs
from jupiter_webapi_client.models.recurring_task_period import RecurringTaskPeriod
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_journals_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.JOURNALS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.JOURNALS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_journal(logged_in_client: AuthenticatedClient):
    def _create_journal(
        right_now: str | None = None,
        period: RecurringTaskPeriod = RecurringTaskPeriod.DAILY,
    ) -> Journal:
        if right_now is None:
            # Use today's date as default
            right_now = pendulum.now().to_iso8601_string()

        result = journal_create_sync(
            client=logged_in_client,
            body=JournalCreateArgs(
                right_now=right_now,
                period=period,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_journal

    return _create_journal


def test_journal_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/journals")

    expect(page.locator("#trunk-panel")).to_contain_text(
        "There are no journals to show"
    )


def test_journal_view_all(page: Page, create_journal) -> None:
    # Create journals for different periods and dates
    journal1 = create_journal(period=RecurringTaskPeriod.DAILY)
    journal2 = create_journal(
        right_now=pendulum.now().subtract(days=1).to_iso8601_string(),
        period=RecurringTaskPeriod.WEEKLY,
    )
    journal3 = create_journal(
        right_now=pendulum.now().subtract(days=7).to_iso8601_string(),
        period=RecurringTaskPeriod.MONTHLY,
    )

    page.goto("/app/workspace/journals")

    # Journals are displayed by their timeline/name, not by ref_id
    # The name is built from the date and period
    expect(page.locator(f"#journal-{journal1.ref_id}")).to_contain_text(
        f"Daily journal for {pendulum.now().format('YYYY-MM-DD')}"
    )
    expect(page.locator(f"#journal-{journal2.ref_id}")).to_contain_text(
        f"Weekly journal for {pendulum.now().subtract(days=1).format('YYYY-MM-DD')}"
    )
    print(pendulum.now().subtract(days=7).to_iso8601_string())
    expect(page.locator(f"#journal-{journal3.ref_id}")).to_contain_text(
        f"Monthly journal for {pendulum.now().subtract(days=7).format('YYYY-MM-DD')}"
    )
