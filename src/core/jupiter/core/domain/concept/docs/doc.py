"""A doc in the docbook."""

import abc

from jupiter.core.domain.concept.docs.doc_idempotency_key import DocIdempotencyKey
from jupiter.core.domain.concept.docs.doc_name import DocName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction


@entity
class Doc(LeafEntity):
    """A doc in the docbook."""

    doc_collection: ParentLink
    parent_doc_ref_id: EntityId | None
    idempotency_key: DocIdempotencyKey
    name: DocName

    note = OwnsOne(Note, domain=NoteDomain.DOC, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_doc(
        ctx: DomainContext,
        doc_collection_ref_id: EntityId,
        parent_doc_ref_id: EntityId | None,
        idempotency_key: DocIdempotencyKey,
        name: DocName,
    ) -> "Doc":
        """Create a doc."""
        return Doc._create(
            ctx,
            doc_collection=ParentLink(doc_collection_ref_id),
            parent_doc_ref_id=parent_doc_ref_id,
            idempotency_key=idempotency_key,
            name=name,
        )

    @update_entity_action
    def change_parent(
        self,
        ctx: DomainContext,
        parent_doc_ref_id: EntityId | None,
    ) -> "Doc":
        """Change the parent doc of the doc."""
        return self._new_version(
            ctx,
            parent_doc_ref_id=parent_doc_ref_id,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[DocName],
    ) -> "Doc":
        """Update the doc name and content."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )


class DocRepository(LeafEntityRepository[Doc], abc.ABC):
    """A repository of docs."""

    @abc.abstractmethod
    async def create_if_not_exists(self, doc: Doc) -> tuple[Doc, bool]:
        """Create a doc if it doesn't exist."""
