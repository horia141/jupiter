import uuid
from dataclasses import dataclass

import pytest


@dataclass
class TestUser:
    __test__ = False  # pytest will ignore this class

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


@pytest.fixture()
def new_random_user() -> TestUser:
    return TestUser.new_random()
