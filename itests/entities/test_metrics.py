"""Tests about metrics."""

import pytest
from jupiter_webapi_client.api.entry.metric_entry_create import (
    sync_detailed as metric_entry_create_sync,
)
from jupiter_webapi_client.api.metrics.metric_create import (
    sync_detailed as metric_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.difficulty import Difficulty
from jupiter_webapi_client.models.eisen import Eisen
from jupiter_webapi_client.models.metric import Metric
from jupiter_webapi_client.models.metric_create_args import MetricCreateArgs
from jupiter_webapi_client.models.metric_entry import MetricEntry
from jupiter_webapi_client.models.metric_entry_create_args import MetricEntryCreateArgs
from jupiter_webapi_client.models.metric_unit import MetricUnit
from jupiter_webapi_client.models.recurring_task_period import RecurringTaskPeriod
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_metrics_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.METRICS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.METRICS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_metric(logged_in_client: AuthenticatedClient):
    def _create_metric(
        name: str,
        is_key: bool = False,
        icon: str | None = None,
        metric_unit: MetricUnit | None = None,
        collection_period: RecurringTaskPeriod | None = None,
        collection_eisen: Eisen | None = None,
        collection_difficulty: Difficulty | None = None,
    ) -> Metric:
        result = metric_create_sync(
            client=logged_in_client,
            body=MetricCreateArgs(
                name=name,
                is_key=is_key,
                icon=icon,
                metric_unit=metric_unit,
                collection_period=collection_period,
                collection_eisen=collection_eisen,
                collection_difficulty=collection_difficulty,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_metric

    return _create_metric


@pytest.fixture(autouse=True, scope="module")
def create_metric_entry(logged_in_client: AuthenticatedClient):
    def _create_metric_entry(
        metric_ref_id: str,
        value: float,
        collection_time: str | None = None,
    ) -> MetricEntry:
        result = metric_entry_create_sync(
            client=logged_in_client,
            body=MetricEntryCreateArgs(
                metric_ref_id=metric_ref_id,
                value=value,
                collection_time=collection_time,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_metric_entry

    return _create_metric_entry


def test_metric_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/metrics")

    expect(page.locator("#trunk-panel")).to_contain_text("There are no metrics to show")


def test_metric_view_all(page: Page, create_metric) -> None:
    metric1 = create_metric("Metric 1")
    metric2 = create_metric("Metric 2", True, "📊", MetricUnit.COUNT)
    metric3 = create_metric(
        "Metric 3",
        False,
        "💰",
        MetricUnit.MONEY,
        RecurringTaskPeriod.DAILY,
        Eisen.IMPORTANT,
        Difficulty.MEDIUM,
    )

    page.goto("/app/workspace/metrics")

    expect(page.locator(f"#metric-{metric1.ref_id}")).to_contain_text("Metric 1")
    expect(page.locator(f"#metric-{metric2.ref_id}")).to_contain_text("Metric 2")
    expect(page.locator(f"#metric-{metric3.ref_id}")).to_contain_text("Metric 3")


def test_metric_view_one_nothing(page: Page, create_metric) -> None:
    metric = create_metric("Metric 1")
    page.goto(f"/app/workspace/metrics/{metric.ref_id}")

    expect(page.locator("#branch-panel")).to_contain_text(
        "There are no metric entries to show"
    )


def test_metric_view_one_entries(
    page: Page, create_metric, create_metric_entry
) -> None:
    metric = create_metric("Metric 1", metric_unit=MetricUnit.COUNT)
    metric_entry1 = create_metric_entry(metric.ref_id, 10.5)
    metric_entry2 = create_metric_entry(metric.ref_id, 25.0, "2024-01-15")

    page.goto(f"/app/workspace/metrics/{metric.ref_id}")
    page.wait_for_selector("#branch-panel")
    expect(page.locator(f"#metric-entry-{metric_entry1.ref_id}")).to_contain_text("10")
    expect(page.locator(f"#metric-entry-{metric_entry2.ref_id}")).to_contain_text("25")
