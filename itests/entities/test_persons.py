"""Tests about persons."""

import pytest
from jupiter_webapi_client.api.persons.person_create import (
    sync_detailed as person_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.person import Person
from jupiter_webapi_client.models.person_create_args import PersonCreateArgs
from jupiter_webapi_client.models.person_relationship import PersonRelationship
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_persons_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.PERSONS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.PERSONS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_person(logged_in_client: AuthenticatedClient):
    def _create_person(name: str, relationship: PersonRelationship) -> Person:
        result = person_create_sync(
            client=logged_in_client,
            body=PersonCreateArgs(name=name, relationship=relationship),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_person

    return _create_person


def test_person_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/persons")

    expect(page.locator("#trunk-panel")).to_contain_text("There are no persons to show")


def test_person_view_all(page: Page, create_person) -> None:
    person1 = create_person("Person 1", PersonRelationship.FAMILY)
    person2 = create_person("Person 2", PersonRelationship.FAMILY)
    person3 = create_person("Person 3", PersonRelationship.FAMILY)

    page.goto("/app/workspace/persons")

    expect(page.locator(f"#person-{person1.ref_id}")).to_contain_text("Person 1")
    expect(page.locator(f"#person-{person2.ref_id}")).to_contain_text("Person 2")
    expect(page.locator(f"#person-{person3.ref_id}")).to_contain_text("Person 3")
