"""Tests about docs."""

import uuid

import pytest
from jupiter_webapi_client.api.docs.doc_create import (
    sync_detailed as doc_create_sync,
)
from jupiter_webapi_client.api.test_helper.workspace_set_feature import (
    sync_detailed as workspace_set_feature_sync,
)
from jupiter_webapi_client.client import AuthenticatedClient
from jupiter_webapi_client.models.doc import Doc
from jupiter_webapi_client.models.doc_create_args import DocCreateArgs
from jupiter_webapi_client.models.paragraph_block import ParagraphBlock
from jupiter_webapi_client.models.paragraph_block_kind import ParagraphBlockKind
from jupiter_webapi_client.models.workspace_feature import WorkspaceFeature
from jupiter_webapi_client.models.workspace_set_feature_args import (
    WorkspaceSetFeatureArgs,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True, scope="module")
def _enable_docs_feature(logged_in_client: AuthenticatedClient):
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.DOCS, value=True),
    )
    yield
    workspace_set_feature_sync(
        client=logged_in_client,
        body=WorkspaceSetFeatureArgs(feature=WorkspaceFeature.DOCS, value=False),
    )


@pytest.fixture(autouse=True, scope="module")
def create_doc(logged_in_client: AuthenticatedClient):
    def _create_doc(
        name: str,
        content: str = "This is a test document.",
        parent_doc_ref_id: str | None = None,
    ) -> Doc:
        # Create a simple paragraph block for the content
        paragraph_block = ParagraphBlock(
            correlation_id=str(uuid.uuid4()),
            kind=ParagraphBlockKind.PARAGRAPH,
            text=content,
        )

        result = doc_create_sync(
            client=logged_in_client,
            body=DocCreateArgs(
                idempotency_key=str(uuid.uuid4()),
                name=name,
                content=[paragraph_block],
                parent_doc_ref_id=parent_doc_ref_id,
            ),
        )
        if result.status_code != 200:
            raise Exception(result.content)
        return result.parsed.new_doc

    return _create_doc


def test_doc_view_nothing(page: Page) -> None:
    page.goto("/app/workspace/docs")

    expect(page.locator("#trunk-panel")).to_contain_text("There are no docs to show")


def test_doc_view_all(page: Page, create_doc) -> None:
    doc1 = create_doc("Doc 1", "This is the first test document.")
    doc2 = create_doc("Doc 2", "This is the second test document.")
    doc3 = create_doc("Doc 3", "This is the third test document.", doc1.ref_id)

    page.goto("/app/workspace/docs")

    expect(page.locator(f"#doc-{doc1.ref_id}")).to_contain_text("Doc 1")
    expect(page.locator(f"#doc-{doc2.ref_id}")).to_contain_text("Doc 2")
    expect(page.locator(f"#doc-{doc3.ref_id}")).to_contain_text("Doc 3")
