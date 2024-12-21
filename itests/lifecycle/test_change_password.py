from jupiter_webapi_client.api.auth.change_password import (
    sync_detailed as change_password,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.change_password_args import ChangePasswordArgs
from jupiter_webapi_client.models.init_result import InitResult
from playwright.sync_api import Page, expect

from itests.conftest import TestUser


def test_change_password(
    page: Page,
    webapi_server_url: str,
    new_user: TestUser,
    new_user_and_workspace: InitResult,
):
    page.goto("/workspace")

    expect(page.locator("body")).to_contain_text("Login")

    page.locator('input[name="emailAddress"]').fill(new_user.email)
    page.locator('input[name="password"]').fill(new_user.password)

    page.locator("#login").click()

    # There's some bizzaro interaction that happens between playwright and its
    # messing about with the browser, and Remix and its taking over of the
    # application communication, and especialy the redirects. If there's no wait
    # here then the redirect from "post /login" with cookies will not work!
    page.wait_for_url("/workspace/*")

    page.locator("#show-sidebar").click()

    page.locator("#account-menu").click()
    page.locator("#security").click()

    page.wait_for_url("/workspace/security")

    page.locator('input[name="currentPassword"]').fill(new_user.password)
    page.locator('input[name="newPassword"]').fill("a-new-password")
    page.locator('input[name="newPasswordRepeat"]').fill("a-new-password")

    page.locator("#change-password").click()

    page.wait_for_url("/workspace/*")

    page.locator("#account-menu").click()
    page.locator("#logout").click()

    page.wait_for_url("/login")

    expect(page.locator("body")).to_contain_text("Login")

    expect(page.locator("body")).to_contain_text("Login")

    page.locator('input[name="emailAddress"]').fill(new_user.email)
    page.locator('input[name="password"]').fill("a-new-password")

    page.locator("#login").click()

    page.wait_for_url("/workspace/*")

    logged_in_client = AuthenticatedClient(
        base_url=webapi_server_url, token=new_user_and_workspace.auth_token_ext
    )

    change_password(
        client=logged_in_client,
        body=ChangePasswordArgs(
            current_password="a-new-password",
            new_password=new_user.password,
            new_password_repeat=new_user.password,
        ),
    )
