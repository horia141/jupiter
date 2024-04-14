"""Tests about vacations."""
from dataclasses import dataclass
import re
import uuid
from playwright.sync_api import Page, expect
import pytest

from itests.conftest import TestUser


def test_vacation_create(page: Page, page_logged_in: TestUser) -> None:
    print(f"Archivatio {page_logged_in.email}")
    page.goto("/workspace/vacations")
    page.locator("#trunk-new-leaf-entty").click()
    page.locator("input[name=\"name\"]").fill("First Vacation")
    page.locator("input[name=\"startDate\"]").fill("2024-12-10")
    page.locator("input[name=\"endDate\"]").fill("2024-12-15")

    expect(page.wait("/workspace/vacations/*"))

def test_vacation_archive(page: Page, page_logged_in: TestUser) -> None:
    page.goto("/workspace/vacations")

    print(f"Archivatio {page_logged_in.email}")
