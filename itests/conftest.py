"""Fixtures for integration tests."""
import uuid
from dataclasses import dataclass

import pytest


@dataclass
class TestUser:
    """A test user."""

    __test__ = False  # pytest will ignore this class

    email: str
    name: str
    password: str

    @staticmethod
    def new_random() -> "TestUser":
        """Create a new random test user."""
        return TestUser(
            email=f"test-{uuid.uuid4()}@example.com",
            name="Test User",
            password="password-123",
        )


@pytest.fixture()
def new_random_user() -> TestUser:
    """Create a new random test user."""
    return TestUser.new_random()
