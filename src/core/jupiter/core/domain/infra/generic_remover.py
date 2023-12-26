"""A generic archiver service."""
import dataclasses
from typing import TypeVar, cast, get_origin

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import CrownEntity, Entity, OwnsLink
from jupiter.core.framework.use_case import ProgressReporter

_EntityT = TypeVar("_EntityT", bound=CrownEntity)


async def generic_remover(
    ctx: DomainContext,
    uow: DomainUnitOfWork,
    progress_reporter: ProgressReporter,
    entity_type: type[CrownEntity],
    ref_id: EntityId,
) -> None:
    """Generic remover for entities."""

    async def _remover(entity: CrownEntity) -> None:
        all_fields = dataclasses.fields(entity)

        for field in all_fields:
            if not isinstance(get_origin(field.type), OwnsLink):
                continue

            value_at_most_one = cast(OwnsLink[Entity], getattr(entity, field.name))
            if CrownEntity not in value_at_most_one.the_type.mro():
                continue
            value_at_most_one_fix = cast(OwnsLink[CrownEntity], value_at_most_one)
            linked_entities = await uow.get_repository(
                value_at_most_one_fix.the_type
            ).find_all_generic(
                allow_archived=True, **value_at_most_one_fix.get_for_entity(entity)
            )

            for linked_entity in linked_entities:
                await _remover(linked_entity)

        await uow.get_repository(entity_type).remove(entity.ref_id)
        await progress_reporter.mark_removed(entity)

    entity = await uow.get_repository(entity_type).load_by_id(ref_id)

    await _remover(entity)
