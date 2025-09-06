"""Tests about projects."""

import pytest
from jupiter_webapi_client.api.get_summaries.get_summaries import (
    sync_detailed as get_summaries_sync,
)
from jupiter_webapi_client.api.projects.project_create import (
    sync_detailed as project_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.get_summaries_args import GetSummariesArgs
from jupiter_webapi_client.models.project import Project
from jupiter_webapi_client.models.project_create_args import ProjectCreateArgs
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_projects_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.PROJECTS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.PROJECTS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def get_root_project_id(logged_in_client: AuthenticatedClient):
    def _get_root_project_id() -> str:
        response = get_summaries_sync(
            client=logged_in_client,
            body=GetSummariesArgs(
                include_projects=True,
            ),
        )
        if response.status_code != 200:
            raise Exception(response.content)
        return response.parsed.root_project.ref_id

    return _get_root_project_id


@pytest.fixture(autouse=True, scope="module")
def create_project(logged_in_client: AuthenticatedClient, get_root_project_id: str):
    def _create_project(name: str, parent_project_ref_id: str | None = None) -> Project:
        if parent_project_ref_id is None:
            parent_project_ref_id = get_root_project_id()

        result = project_create_sync(
            client=logged_in_client,
            body=ProjectCreateArgs(
                name=name,
                parent_project_ref_id=parent_project_ref_id,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_project

    return _create_project


def test_project_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/projects")

    # Projects always has at least the root project, so we check for the root project instead
    expect(page.locator("#trunk-panel")).to_contain_text("Root Project")


def test_project_view_all(page: Page, create_project) -> None:
    project1 = create_project("Project 1")
    project2 = create_project("Project 2")
    project3 = create_project("Project 3", project1.ref_id)

    page.goto("/app/workspace/projects")

    expect(page.locator(f"#project-{project1.ref_id}")).to_contain_text("Project 1")
    expect(page.locator(f"#project-{project2.ref_id}")).to_contain_text("Project 2")
    expect(page.locator(f"#project-{project3.ref_id}")).to_contain_text("Project 3")
