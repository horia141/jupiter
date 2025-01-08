from jupiter.core.use_cases.application.init import InitResult
from playwright.sync_api import Page, expect

from itests.conftest import TestUser


def test_close_account(
    page: Page,
    webapi_server_url: str,
    new_user: TestUser,
    new_user_and_workspace: InitResult,
) -> None:
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

    page.goto("/workspace/account")

    page.locator("#close-account-initialize").click()
    page.locator("#close-account").click()

    page.wait_for_url("/init")
