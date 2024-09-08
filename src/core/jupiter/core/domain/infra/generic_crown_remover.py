"""A generic archiver service."""
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import CrownEntity, LeafSupportEntity, OwnsLink
from jupiter.core.framework.use_case import ProgressReporter


async def generic_crown_remover(
    ctx: DomainContext,
    uow: DomainUnitOfWork,
    progress_reporter: ProgressReporter,
    entity_type: type[CrownEntity],
    ref_id: EntityId,
) -> None:
    """Generic remover for entities."""

    async def _remover(entity: CrownEntity) -> None:
        for field in entity.__class__.__dict__.values():
            if not isinstance(field, OwnsLink):
                continue
            if not issubclass(field.the_type, CrownEntity):
                raise Exception(
                    f"Entity {entity.__class__} owns an non-crown entity {field.the_type}"
                )
            linked_entities = await uow.get_for(field.the_type).find_all_generic(
                parent_ref_id=None, allow_archived=True, **field.get_for_entity(entity)
            )

            for linked_entity in linked_entities:
                await _remover(linked_entity)

        if entity.is_safe_to_archive:
            await uow.get_for(entity.__class__).remove(entity.ref_id)
            if not isinstance(entity, LeafSupportEntity):
                await progress_reporter.mark_removed(entity)

    entity = await uow.get_for(entity_type).load_by_id(ref_id, allow_archived=True)

    await _remover(entity)
