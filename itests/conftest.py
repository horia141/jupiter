"""Fixtures for integration tests."""
import os
import re
import uuid
from dataclasses import dataclass

import pytest
import validators


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


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


@pytest.fixture(autouse=True, scope="package")
def webapi_server_url() -> str:
    """The URL of the local Web API server."""
    local_webapi_server_url = os.getenv("LOCAL_OR_SELF_HOSTED_WEBAPI_SERVER_URL")
    if re.match(r"^http://0[.]0[.]0[.]0:\d+$", local_webapi_server_url):
        return local_webapi_server_url
    validation_result = validators.url(local_webapi_server_url)
    if validation_result is not True:
        raise Exception(f"Invalid Web API URL '{local_webapi_server_url}'")
    return local_webapi_server_url
