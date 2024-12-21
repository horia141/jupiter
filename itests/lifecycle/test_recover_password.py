import re

from jupiter_webapi_client.api.auth.change_password import (
    sync_detailed as change_password,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.change_password_args import ChangePasswordArgs
from jupiter_webapi_client.models.init_result import InitResult
from playwright.sync_api import Page, expect

from itests.conftest import TestUser


def test_recover_password(
    page: Page,
    new_user: TestUser,
    webapi_server_url: str,
    new_user_and_workspace: InitResult,
):
    page.goto("/workspace")

    page.locator("#reset-password").click()

    page.locator('input[name="emailAddress"]').fill(new_user.email)
    page.locator('input[name="recoveryToken"]').fill(
        new_user_and_workspace.recovery_token
    )
    page.locator('input[name="newPassword"]').fill("a-new-password")
    page.locator('input[name="newPasswordRepeat"]').fill("a-new-password")

    page.locator("#reset-password").click()

    page.get_by_role("link", name="To Workspace").click()

    expect(page.locator("#trunk-panel-content")).to_contain_text(
        re.compile("There are no inbox tasks to show")
    )

    logged_in_client = AuthenticatedClient(
        base_url=webapi_server_url, token=new_user_and_workspace.auth_token_ext
    )

    change_password(
        client=logged_in_client,
        body=ChangePasswordArgs(
            current_password="a-new-password",
            new_password=new_user.password,
            new_password_repeat=new_user.password,
        ),
    )
