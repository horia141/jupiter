"""Tests for the working mem."""
from playwright.sync_api import Page

from itests.conftest import TestUser


def test_working_mem_write(page: Page, new_random_user: TestUser) -> None:
    page.goto("/app/workspace/working-mem")

    print(f"Working mem {new_random_user.email}")
