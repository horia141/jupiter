"""Tests about smart lists."""

import pytest
from jupiter_webapi_client.api.item.smart_list_item_create import (
    sync_detailed as smart_list_item_create_sync,
)
from jupiter_webapi_client.api.smart_lists.smart_list_create import (
    sync_detailed as smart_list_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.smart_list import SmartList
from jupiter_webapi_client.models.smart_list_create_args import SmartListCreateArgs
from jupiter_webapi_client.models.smart_list_item import SmartListItem
from jupiter_webapi_client.models.smart_list_item_create_args import (
    SmartListItemCreateArgs,
)
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_smart_lists_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.SMART_LISTS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.SMART_LISTS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_smart_list(logged_in_client: AuthenticatedClient):
    def _create_smart_list(name: str, icon: str | None = None) -> SmartList:
        result = smart_list_create_sync(
            client=logged_in_client,
            body=SmartListCreateArgs(
                name=name,
                icon=icon,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_smart_list

    return _create_smart_list


@pytest.fixture(autouse=True, scope="module")
def create_smart_list_item(logged_in_client: AuthenticatedClient):
    def _create_smart_list_item(name: str, smart_list_ref_id: str) -> SmartListItem:
        result = smart_list_item_create_sync(
            client=logged_in_client,
            body=SmartListItemCreateArgs(
                name=name,
                smart_list_ref_id=smart_list_ref_id,
                is_done=False,
                tag_names=[],
                url=None,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_smart_list_item

    return _create_smart_list_item


def test_smart_list_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/smart-lists")

    expect(page.locator("#trunk-panel")).to_contain_text(
        "There are no smart lists to show"
    )


def test_smart_list_view_all(page: Page, create_smart_list) -> None:
    smart_list1 = create_smart_list("Smart List 1")
    smart_list2 = create_smart_list("Smart List 2", "📝")
    smart_list3 = create_smart_list("Smart List 3", "⭐")

    page.goto("/app/workspace/smart-lists")

    expect(page.locator(f"#smart-list-{smart_list1.ref_id}")).to_contain_text(
        "Smart List 1"
    )
    expect(page.locator(f"#smart-list-{smart_list2.ref_id}")).to_contain_text(
        "Smart List 2"
    )
    expect(page.locator(f"#smart-list-{smart_list3.ref_id}")).to_contain_text(
        "Smart List 3"
    )


def test_smart_list_view_one_nothing(page: Page, create_smart_list) -> None:
    smart_list = create_smart_list("Smart List 1")
    page.goto(f"/app/workspace/smart-lists/{smart_list.ref_id}/items")

    expect(page.locator("#branch-panel")).to_contain_text("There are no items to show")


def test_smart_list_view_one_items(
    page: Page, create_smart_list, create_smart_list_item
) -> None:
    smart_list = create_smart_list("Smart List 1")
    smart_list_item1 = create_smart_list_item("Smart List Item 1", smart_list.ref_id)
    smart_list_item2 = create_smart_list_item("Smart List Item 2", smart_list.ref_id)

    page.goto(f"/app/workspace/smart-lists/{smart_list.ref_id}/items")
    page.wait_for_selector("#branch-panel")
    expect(page.locator(f"#smart-list-item-{smart_list_item1.ref_id}")).to_contain_text(
        "Smart List Item 1"
    )
    expect(page.locator(f"#smart-list-item-{smart_list_item2.ref_id}")).to_contain_text(
        "Smart List Item 2"
    )
