"""Fixtures with auth sessions."""
import re

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from itests.conftest import TestUser


@pytest.fixture(autouse=True, scope="package")
def logged_in_user(browser: Browser, base_url: str) -> TestUser:
    new_random_user = TestUser.new_random()

    browser_context = browser.new_context()
    page = browser_context.new_page()

    page.goto(base_url)

    page.get_by_role("link", name="Go To The Workspace").click()
    page.locator('input[name="emailAddress"]').click()
    page.get_by_role("link", name="New Workspace").click()
    page.locator('input[name="userEmailAddress"]').fill(new_random_user.email)
    page.locator('input[name="userName"]').fill(new_random_user.name)
    page.locator('input[name="authPassword"]').fill(new_random_user.password)
    page.locator('input[name="authPasswordRepeat"]').fill(new_random_user.password)
    page.get_by_role("button", name="Create").click()
    page.get_by_role("link", name="To Workspace").click()

    expect(page.locator("#trunk-panel-content")).to_contain_text(
        re.compile("There are no inbox tasks to show")
    )

    page.close()

    return new_random_user


@pytest.fixture(autouse=True)
def page_logged_in(
    context: BrowserContext, page: Page, logged_in_user: TestUser
) -> TestUser:
    page.goto("/login")

    page.locator('input[name="emailAddress"]').fill(logged_in_user.email)
    page.locator('input[name="password"]').fill(logged_in_user.password)

    page.locator("#login").click()

    # There's some bizzaro interaction that happens between playwright and its
    # messing about with the browser, and Remix and its taking over of the
    # application communication, and especialy the redirects. If there's no wait
    # here then the redirect from "post /login" with cookies will not work!
    page.wait_for_url("/workspace/*")

    return logged_in_user
