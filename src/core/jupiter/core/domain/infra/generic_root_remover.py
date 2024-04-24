"""A generic archiver service."""
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsLink,
    CrownEntity,
    Entity,
    LeafSupportEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.record import ContainsRecords, Record
from jupiter.core.framework.use_case import ProgressReporter


async def generic_root_remover(
    ctx: DomainContext,
    uow: DomainUnitOfWork,
    progress_reporter: ProgressReporter,
    entity_type: type[RootEntity],
    ref_id: EntityId,
) -> None:
    """Removes all crown entities starting from a root, but leaves trunks and stubs alone."""

    async def _remover(entity: Entity) -> None:
        for field in entity.__class__.__dict__.values():
            if not isinstance(field, ContainsLink) and not isinstance(
                field, ContainsRecords
            ):
                continue

            if issubclass(field.the_type, TrunkEntity):
                linked_trunk_entity = await uow.get_for(field.the_type).load_by_parent(
                    entity.ref_id
                )

                await _remover(linked_trunk_entity)
            elif issubclass(field.the_type, StubEntity):
                linked_stub_entity = await uow.get_for(field.the_type).load_by_parent(
                    entity.ref_id
                )

                await _remover(linked_stub_entity)
            elif issubclass(field.the_type, CrownEntity):
                linked_entities = await uow.get_for(field.the_type).find_all(
                    parent_ref_id=entity.ref_id, allow_archived=False
                )

                for linked_entity in linked_entities:
                    await _remover(linked_entity)
            elif issubclass(field.the_type, Record):
                linked_records = await uow.get_for_record(field.the_type).find_all(
                    entity.ref_id,
                )

                for linked_record in linked_records:
                    await uow.get_for_record(field.the_type).remove(linked_record)
            else:
                raise Exception(f"Unsupported field type {field.the_type}")

        if isinstance(entity, CrownEntity) and entity.is_safe_to_archive:
            await uow.get_for(entity.__class__).remove(entity.ref_id)
            if not isinstance(entity, LeafSupportEntity):
                await progress_reporter.mark_removed(entity)

    entity = await uow.get_for(entity_type).load_by_id(ref_id)
    await _remover(entity)
