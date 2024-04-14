"""Fixtures with auth sessions."""
from dataclasses import dataclass
import os
import re
import time
import uuid
from playwright.sync_api import Page, expect, Browser, BrowserContext
import pytest

from itests.conftest import TestUser

from rich import print
    

@pytest.fixture(autouse=True, scope="package")
def logged_in_user(browser: Browser, base_url: str) -> TestUser:
    new_random_user = TestUser.new_random()

    browser_context = browser.new_context()
    page = browser_context.new_page()

    page.goto(base_url)


    print(browser_context.cookies())

    page.get_by_role("link", name="Go To The Workspace").click()
    page.locator("input[name=\"emailAddress\"]").click()
    page.get_by_role("link", name="New Workspace").click()
    page.locator("input[name=\"userEmailAddress\"]").fill(new_random_user.email)
    page.locator("input[name=\"userName\"]").fill(new_random_user.name)
    page.locator("input[name=\"authPassword\"]").fill(new_random_user.password)
    page.locator("input[name=\"authPasswordRepeat\"]").fill(new_random_user.password)
    page.get_by_role("button", name="Create").click()
    page.get_by_role("link", name="To Workspace").click()

    expect(page.locator("#trunk-panel-content")).to_contain_text(re.compile("There are no inbox tasks to show"))

    print(browser_context.cookies())

    page.close()

    yield new_random_user

@pytest.fixture(autouse=True, scope="function")
def page_logged_in(context: BrowserContext, page: Page, logged_in_user: TestUser) -> TestUser:
    page.goto("/login")

    print(context.cookies())

    page.locator("input[name=\"emailAddress\"]").click()
    page.locator("input[name=\"emailAddress\"]").fill(logged_in_user.email)
    page.locator("input[name=\"password\"]").click()
    page.locator("input[name=\"password\"]").fill(logged_in_user.password)

    time.sleep(3)

    page.locator("#login").click()

    print(context.cookies())

    yield logged_in_user
