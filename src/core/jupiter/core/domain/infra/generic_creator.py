"""A generic creator of entities."""
from typing import TypeVar

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.entity import CrownEntity, LeafSupportEntity
from jupiter.core.framework.use_case import ProgressReporter

_EntityT = TypeVar("_EntityT", bound=CrownEntity)


async def generic_creator(
    uow: DomainUnitOfWork,
    progress_reporter: ProgressReporter,
    entity: _EntityT,
) -> _EntityT:
    """Create an entity."""
    entity = await uow.get_repository(type(entity)).create(entity)
    if not isinstance(entity, LeafSupportEntity):
        await progress_reporter.mark_created(entity)
    return entity
