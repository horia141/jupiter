import pytest
from playwright.sync_api import Page, expect

from itests.conftest import TestUser


def test_login(page: Page, new_user: TestUser):
    page.goto("/app/workspace")

    expect(page.locator("body")).to_contain_text("Login")

    page.locator('input[name="emailAddress"]').fill(new_user.email)
    page.locator('input[name="password"]').fill(new_user.password)

    page.locator("#login").click()

    # There's some bizzaro interaction that happens between playwright and its
    # messing about with the browser, and Remix and its taking over of the
    # application communication, and especialy the redirects. If there's no wait
    # here then the redirect from "post /login" with cookies will not work!
    page.wait_for_url("/app/workspace/*")


def test_login_bad_user_name(
    page: Page, new_user: TestUser, pytestconfig: pytest.Config
):
    page.goto("/app/workspace")

    expect(page.locator("body")).to_contain_text("Login")

    page.locator('input[name="emailAddress"]').fill("bad-username@example.com")
    page.locator('input[name="password"]').fill(new_user.password)

    page.locator("#login").click()

    expect(page.locator("body")).to_contain_text("User email or password invalid")


def test_login_bad_password(page: Page, new_user: TestUser):
    page.goto("/app/workspace")

    expect(page.locator("body")).to_contain_text("Login")

    page.locator('input[name="emailAddress"]').fill(new_user.email)
    page.locator('input[name="password"]').fill("a bad password")

    page.locator("#login").click()

    expect(page.locator("body")).to_contain_text("User email or password invalid")
