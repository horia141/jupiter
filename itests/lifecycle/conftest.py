"""Fixtures for lifecycle tests."""
from typing import Iterator

import pytest
from jupiter.core.domain.features import (
    BASIC_USER_FEATURE_FLAGS_ARR,
    BASIC_WORKSPACE_FEATURE_FLAGS_ARR,
)
from jupiter_webapi_client import Client
from jupiter_webapi_client.api.application.init import sync_detailed as init_sync
from jupiter_webapi_client.api.test_helper.clear_all import (
    sync_detailed as clear_all_sync,
)
from jupiter_webapi_client.api.test_helper.remove_all import (
    sync_detailed as remove_all_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.clear_all_args import ClearAllArgs
from jupiter_webapi_client.models.init_args import InitArgs
from jupiter_webapi_client.models.init_result import InitResult
from jupiter_webapi_client.models.remove_all_args import RemoveAllArgs

from itests.conftest import TestUser


@pytest.fixture(autouse=True, scope="package")
def new_user() -> TestUser:
    """Create a new random test user."""
    return TestUser.new_random()


@pytest.fixture(autouse=True, scope="package")
def new_user_and_workspace(
    webapi_server_url: str, new_user: TestUser
) -> Iterator[InitResult]:
    """Create a new user and workspace."""
    guest_client = Client(base_url=webapi_server_url)

    init_response = init_sync(
        client=guest_client,
        body=InitArgs(
            for_app_review=False,
            user_email_address=new_user.email,
            user_name=new_user.name,
            user_timezone="UTC",
            user_feature_flags=BASIC_USER_FEATURE_FLAGS_ARR,
            auth_password=new_user.password,
            auth_password_repeat=new_user.password,
            workspace_name="Test Workspace",
            workspace_root_project_name="Root Project",
            workspace_first_schedule_stream_name="Life",
            workspace_feature_flags=BASIC_WORKSPACE_FEATURE_FLAGS_ARR,
        ),
    )
    if init_response.status_code != 200:
        raise Exception(init_response.content)

    logged_in_client = AuthenticatedClient(
        base_url=webapi_server_url, token=init_response.parsed.auth_token_ext
    )

    yield init_response.parsed

    clear_all_sync(
        client=logged_in_client,
        body=ClearAllArgs(
            user_name=new_user.name,
            user_timezone="UTC",
            auth_current_password=new_user.password,
            auth_new_password=new_user.password,
            auth_new_password_repeat=new_user.password,
            workspace_name="Test Workspace",
            workspace_root_project_name="Root Project",
        ),
    )

    remove_all_sync(client=logged_in_client, body=RemoveAllArgs())
