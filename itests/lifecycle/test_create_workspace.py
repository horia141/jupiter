from dataclasses import dataclass
import re
import uuid
from playwright.sync_api import Page, expect
import pytest

from itests.conftest import TestUser

def test_create_workspace(page: Page, new_random_user: TestUser) -> None:
    page.goto("/")

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
