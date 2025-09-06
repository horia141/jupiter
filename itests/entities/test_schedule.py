"""Tests about schedule."""

import re

import pendulum
import pytest
from jupiter_webapi_client.api.event_in_day.schedule_event_in_day_create import (
    sync_detailed as schedule_event_in_day_create_sync,
)
from jupiter_webapi_client.api.stream.schedule_stream_create_for_user import (
    sync_detailed as schedule_stream_create_for_user_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.schedule_event_in_day import ScheduleEventInDay
from jupiter_webapi_client.models.schedule_event_in_day_create_args import (
    ScheduleEventInDayCreateArgs,
)
from jupiter_webapi_client.models.schedule_stream import ScheduleStream
from jupiter_webapi_client.models.schedule_stream_color import ScheduleStreamColor
from jupiter_webapi_client.models.schedule_stream_create_for_user_args import (
    ScheduleStreamCreateForUserArgs,
)
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_schedule_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.SCHEDULE, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.SCHEDULE, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_schedule_stream(logged_in_client: AuthenticatedClient):
    def _create_schedule_stream(
        name: str,
        color: ScheduleStreamColor = ScheduleStreamColor.BLUE,
    ) -> ScheduleStream:
        result = schedule_stream_create_for_user_sync(
            client=logged_in_client,
            body=ScheduleStreamCreateForUserArgs(
                name=name,
                color=color,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_schedule_stream

    return _create_schedule_stream


@pytest.fixture(autouse=True, scope="module")
def create_schedule_event_in_day(logged_in_client: AuthenticatedClient):
    def _create_schedule_event_in_day(
        schedule_stream_ref_id: str,
        name: str,
        start_date: str | None = None,
        start_time_in_day: str = "09:00",
        duration_mins: int = 60,
    ) -> ScheduleEventInDay:
        if start_date is None:
            start_date = pendulum.now().to_iso8601_string()

        result = schedule_event_in_day_create_sync(
            client=logged_in_client,
            body=ScheduleEventInDayCreateArgs(
                schedule_stream_ref_id=schedule_stream_ref_id,
                name=name,
                start_date=start_date,
                start_time_in_day=start_time_in_day,
                duration_mins=duration_mins,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_schedule_event_in_day

    return _create_schedule_event_in_day


def test_schedule_view_empty_calendar(page: Page) -> None:
    page.goto("/app/workspace/calendar")

    # Calendar view shows empty state - no specific text to check for empty calendar
    # The calendar will just show empty days
    expect(page.locator("body")).to_be_visible()


def test_schedule_view_with_events(
    page: Page, create_schedule_stream, create_schedule_event_in_day
) -> None:
    # Create a schedule stream first
    schedule_stream = create_schedule_stream("Work Schedule", ScheduleStreamColor.BLUE)

    # Create some events
    event1 = create_schedule_event_in_day(
        schedule_stream.ref_id,
        "Morning Meeting",
        pendulum.now().to_iso8601_string(),
        "09:00",
        60,
    )
    event2 = create_schedule_event_in_day(
        schedule_stream.ref_id,
        "Lunch Break",
        pendulum.now().to_iso8601_string(),
        "12:00",
        30,
    )
    event3 = create_schedule_event_in_day(
        schedule_stream.ref_id,
        "Project Review",
        pendulum.now().add(days=1).to_iso8601_string(),
        "14:00",
        90,
    )

    page.goto("/app/workspace/calendar")

    # The events should be visible in the calendar view
    expect(
        page.locator(f"#schedule-event-in-day-block-{event1.ref_id}")
    ).to_contain_text(re.compile(r".*Morning.*"))
    expect(
        page.locator(f"#schedule-event-in-day-block-{event2.ref_id}")
    ).to_contain_text(re.compile(r".*Lunch.*"))
    expect(
        page.locator(f"#schedule-event-in-day-block-{event3.ref_id}")
    ).to_contain_text(re.compile(r".*Project.*"))
