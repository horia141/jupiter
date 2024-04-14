from dataclasses import dataclass
import re
import uuid
from playwright.sync_api import Page, expect
import pytest

@dataclass
class TestUser:
    __test__ = False # pytest will ignore this class

    email: str
    name: str
    password: str

    @staticmethod
    def new_random() -> "TestUser":
        return TestUser(
            email=f"test-{uuid.uuid4()}@example.com",
            name="Test User",
            password="password-123",
        )

@pytest.fixture
def new_random_user() -> TestUser:
    return TestUser(
        email=f"horia-{uuid.uuid4()}@example.com",
        name="Horia",
        password="password-123",
    )
