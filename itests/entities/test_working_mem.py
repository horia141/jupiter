"""Tests for the working mem."""
from dataclasses import dataclass
import re
import uuid
from playwright.sync_api import Page, expect
import pytest

from itests.conftest import TestUser

def test_working_mem_write(page: Page, new_random_user: TestUser) -> None:
    page.goto("/workspace/working-mem")

    print(f"Working mem {new_random_user.email}")