"""Tests about vacations."""
import re
import time
from collections.abc import Iterator

import pytest
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.api.vacations.vacation_create import (
    sync_detailed as vacation_create_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.vacation import Vacation
from jupiter_webapi_client.models.vacation_create_args import VacationCreateArgs
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Browser, Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_vacations_feature(logged_in_client: AuthenticatedClient) -> Iterator[None]:
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.VACATIONS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.VACATIONS, value=False),
    )


@pytest.fixture()
def create_vacation(logged_in_client: AuthenticatedClient):
    def _create_vacation(
        name: str, start_month: int, start_day: int, end_month: int, end_day: int
    ) -> Vacation:
        result = vacation_create_sync(
            client=logged_in_client,
            body=VacationCreateArgs(
                name=name,
                start_date=f"2024-{start_month}-{start_day}",
                end_date=f"2024-{end_month}-{end_day}",
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_vacation

    return _create_vacation


def test_vacation_view_all(
    logged_in_client: AuthenticatedClient, page: Page, create_vacation
) -> None:
    vacation1 = create_vacation("First Vacation", 12, 10, 12, 15)
    vacation2 = create_vacation("Second Vacation", 12, 20, 12, 25)
    vacation3 = create_vacation("Third Vacation", 12, 22, 12, 27)

    page.goto("/workspace/vacations")

    expect(page.locator(f"#vacation-{vacation1.ref_id}")).to_contain_text(
        "First Vacation"
    )
    expect(page.locator(f"#vacation-{vacation2.ref_id}")).to_contain_text(
        "Second Vacation"
    )
    expect(page.locator(f"#vacation-{vacation3.ref_id}")).to_contain_text(
        "Third Vacation"
    )


def test_vacation_view_one(page: Page, create_vacation) -> None:
    vacation = create_vacation("First Vacation", 12, 10, 12, 15)
    page.goto(f"/workspace/vacations/{vacation.ref_id}")
    page.wait_for_selector("#leaf-panel")

    expect(page.locator('input[name="name"]')).to_have_value("First Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-10")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-15")


def test_vacation_create(page: Page, browser: Browser) -> None:
    page.goto("/workspace/vacations")
    page.wait_for_selector("#trunk-panel")
    page.locator("#trunk-new-leaf-entity").click()
    page.locator('input[name="name"]').fill("First Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-10")
    page.locator('input[name="endDate"]').fill("2024-12-15")

    page.locator("#vacation-create").click()

    page.wait_for_url(re.compile(r"/workspace/vacations/\d+"))

    expect(page.locator('input[name="name"]')).to_have_value("First Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-10")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-15")

    entity_id = page.url.split("/")[-1]
    expect(page.locator(f"#vacation-{entity_id}")).to_contain_text("First Vacation")


def test_vacation_update(page: Page, create_vacation) -> None:
    vacation = create_vacation("First Vacation", 12, 10, 12, 15)

    page.goto(f"/workspace/vacations/{vacation.ref_id}")
    page.wait_for_selector("#leaf-panel")

    page.locator('input[name="name"]').fill("Updated Vacation")
    page.locator('input[name="startDate"]').fill("2024-12-11")
    page.locator('input[name="endDate"]').fill("2024-12-16")

    page.locator("#vacation-update").click()

    page.wait_for_url(re.compile(r"/workspace/vacations/\d+"))
    page.wait_for_selector("#leaf-panel")

    expect(page.locator('input[name="name"]')).to_have_value("Updated Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-11")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-16")

    page.reload()
    page.wait_for_selector("#leaf-panel")

    expect(page.locator('input[name="name"]')).to_have_value("Updated Vacation")
    expect(page.locator('input[name="startDate"]')).to_have_value("2024-12-11")
    expect(page.locator('input[name="endDate"]')).to_have_value("2024-12-16")

    entity_id = page.url.split("/")[-1]
    expect(page.locator(f"#vacation-{entity_id}")).to_contain_text("Updated Vacation")


def test_vacation_create_note(page: Page, create_vacation) -> None:
    vacation = create_vacation("First Vacation", 12, 10, 12, 15)
    page.goto(f"/workspace/vacations/{vacation.ref_id}")
    page.wait_for_selector("#leaf-panel")

    page.locator("#vacation-create-note").click()
    page.wait_for_selector("#entity-block-editor")

    page.locator('#editorjs div[contenteditable="true"]').first.fill("This is a note.")

    page.wait_for_url("/workspace/vacations/*")

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )
    time.sleep(1)  # Wait for the update to be saved.

    page.reload()

    page.wait_for_selector("#leaf-panel")

    expect(page.locator('#editorjs div[contenteditable="true"]').first).to_contain_text(
        "This is a note."
    )


def test_vacation_archive(page: Page, create_vacation) -> None:
    vacation = create_vacation("First Vacation", 12, 10, 12, 15)
    page.goto(f"/workspace/vacations/{vacation.ref_id}")
    page.wait_for_selector("#leaf-panel")

    page.locator("#leaf-entity-archive").click()

    expect(page.locator('input[name="name"]')).not_to_be_disabled()
    expect(page.locator('input[name="startDate"]')).not_to_be_disabled()
    expect(page.locator('input[name="endDate"]')).not_to_be_disabled()

    expect(page.locator("#vacation-update")).to_be_disabled()
    expect(page.locator("#vacation-create-note")).to_be_disabled()
    expect(page.locator("#leaf-entity-archive")).to_be_disabled()

    entity_id = page.url.split("/")[-1]
    expect(page.locator(f"#vacation-{entity_id}")).to_have_count(0)
