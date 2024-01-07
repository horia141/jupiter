"""A generic archiver service."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import CrownEntity, LeafSupportEntity, OwnsLink
from jupiter.core.framework.use_case import ProgressReporter


async def generic_archiver(
    ctx: DomainContext,
    uow: DomainUnitOfWork,
    progress_reporter: ProgressReporter,
    entity_type: type[CrownEntity],
    ref_id: EntityId,
) -> None:
    """Generic archiver for entities."""

    async def _archiver(entity: CrownEntity) -> None:
        if entity.archived:
            return
        entity = entity.mark_archived(ctx)
        await uow.get_repository(entity.__class__).save(entity)
        if not isinstance(entity, LeafSupportEntity):
            await progress_reporter.mark_updated(entity)

        for field in entity.__class__.__dict__.values():
            if not isinstance(field, OwnsLink):
                continue
            linked_entities = await uow.get_repository(field.the_type).find_all_generic(
                allow_archived=False, **field.get_for_entity(entity)
            )

            for linked_entity in linked_entities:
                await _archiver(linked_entity)

    entity = await uow.get_repository(entity_type).load_by_id(ref_id)

    await _archiver(entity)
