"""Tests about vacations."""
from dataclasses import dataclass
import re
import uuid
from playwright.sync_api import Page, expect
import pytest

from itests.conftest import TestUser


def test_vacation_create(page: Page, new_random_user: TestUser) -> None:
    page.goto("/workspace/vacations")

    print(f"Creatio {new_random_user.email}")

def test_vacation_archive(page: Page, new_random_user: TestUser) -> None:
    page.goto("/workspace/vacations")

    print(f"Archivatio {new_random_user.email}")
