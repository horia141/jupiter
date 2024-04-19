"""Fixtures with auth sessions."""
from collections.abc import Iterator
import re
import sys
from typing import Any, Generator

from jupiter.core.domain.features import BASIC_USER_FEATURE_FLAGS_ARR, BASIC_WORKSPACE_FEATURE_FLAGS_ARR, UserFeature, WorkspaceFeature
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from itests.conftest import TestUser
from jupiter_webapi_client import Client
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.clear_all_args import ClearAllArgs
from jupiter_webapi_client.models.init_args import InitArgs
from jupiter_webapi_client.api.init.init import sync_detailed as init_sync
from jupiter_webapi_client.api.test_helper.remove_all import sync_detailed as remove_all_sync
from jupiter_webapi_client.api.test_helper.clear_all import sync_detailed as clear_all_sync
from jupiter_webapi_client.models.remove_all_args import RemoveAllArgs


@pytest.fixture(autouse=True, scope="package")
def logged_in_user(browser: Browser, base_url: str) -> Iterator[tuple[AuthenticatedClient, TestUser]]:

    new_random_user = TestUser.new_random()

    guest_client = Client(base_url="http://localhost:8010") # TODO: fix this

    init_response = init_sync(
        client=guest_client, 
        body=InitArgs(
            user_email_address=new_random_user.email,
            user_name=new_random_user.name,
            user_timezone="UTC",
            user_feature_flags=BASIC_USER_FEATURE_FLAGS_ARR,
            auth_password=new_random_user.password,
            auth_password_repeat=new_random_user.password,
            workspace_name="Test Workspace",
            workspace_root_project_name="Root Project",
            workspace_feature_flags=BASIC_WORKSPACE_FEATURE_FLAGS_ARR
        ))
    if init_response.status_code != 200:
        raise Exception(init_response.content)
    
    logged_in_client = AuthenticatedClient(base_url="http://localhost:8010", token=init_response.parsed.auth_token_ext)

    yield logged_in_client, new_random_user

    remove_all_sync(client=logged_in_client, body=RemoveAllArgs())


@pytest.fixture(autouse=True)
def page_logged_in(
    context: BrowserContext, page: Page, logged_in_user: tuple[AuthenticatedClient, TestUser]
) -> Iterator[TestUser]:
    page.goto("/login")

    page.locator('input[name="emailAddress"]').fill(logged_in_user[1].email)
    page.locator('input[name="password"]').fill(logged_in_user[1].password)

    page.locator("#login").click()

    # There's some bizzaro interaction that happens between playwright and its
    # messing about with the browser, and Remix and its taking over of the
    # application communication, and especialy the redirects. If there's no wait
    # here then the redirect from "post /login" with cookies will not work!
    page.wait_for_url("/workspace/*")

    yield logged_in_user

    clear_all_sync(client=logged_in_user[0], body=ClearAllArgs(
            user_name=logged_in_user[1].name,
            user_timezone="UTC",
            auth_current_password=logged_in_user[1].password,
            auth_new_password=logged_in_user[1].password,
            auth_new_password_repeat=logged_in_user[1].password,
            workspace_name="Test Workspace",
            workspace_root_project_name="Root Project",
    ))
