"""A generic archiver service."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsLink,
    CrownEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.record import ContainsRecords, Record


async def generic_full_archiver(
    ctx: DomainContext,
    uow: DomainUnitOfWork,
    entity_type: type[RootEntity],
    ref_id: EntityId,
) -> None:
    """Archives all entities descending from a given root, no exceptions."""

    async def _archiver(
        entity: RootEntity | TrunkEntity | StubEntity | CrownEntity,
    ) -> None:
        if entity.archived:
            return
        if entity.is_safe_to_archive:
            entity = entity.mark_archived(ctx)
            # Typing is faulty here, as it can't map A|B|C|D to
            # save(A) or save(B) or save(C) or save(D)
            await uow.get_for(entity.__class__).save(entity)  # type: ignore

        for field in entity.__class__.__dict__.values():
            if not isinstance(field, ContainsLink) and not isinstance(
                field, ContainsRecords
            ):
                continue

            if issubclass(field.the_type, TrunkEntity):
                linked_trunk_entity = await uow.get_for(field.the_type).load_by_parent(
                    entity.ref_id
                )

                await _archiver(linked_trunk_entity)
            elif issubclass(field.the_type, StubEntity):
                linked_stub_entity = await uow.get_for(field.the_type).load_by_parent(
                    entity.ref_id
                )

                await _archiver(linked_stub_entity)
            elif issubclass(field.the_type, CrownEntity):
                linked_entities = await uow.get_for(field.the_type).find_all(
                    parent_ref_id=entity.ref_id, allow_archived=False
                )

                for linked_entity in linked_entities:
                    await _archiver(linked_entity)
            elif issubclass(field.the_type, Record):
                linked_records = await uow.get_for_record(field.the_type).find_all(
                    entity.ref_id,
                )

                for linked_record in linked_records:
                    await uow.get_for_record(field.the_type).remove(linked_record)
            else:
                raise Exception(f"Unsupported field type {field.the_type}")

    entity = await uow.get_for(entity_type).load_by_id(ref_id)
    await _archiver(entity)
