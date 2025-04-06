"""A generic finder for entities."""

from collections.abc import Iterable
from typing import TypeVar, overload

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import CrownEntity, EntityLink

_EntityT = TypeVar("_EntityT", bound=CrownEntity)
_LinkedEntity1T = TypeVar("_LinkedEntity1T", bound=CrownEntity)
_LinkedEntity2T = TypeVar("_LinkedEntity2T", bound=CrownEntity)


@overload
async def generic_finder(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    *,
    allow_archived: bool = False
) -> _EntityT:
    pass


@overload
async def generic_finder(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: EntityLink[_LinkedEntity1T],
    *,
    allow_archived: bool = False
) -> tuple[_EntityT, Iterable[_LinkedEntity1T]]:
    pass


@overload
async def generic_finder(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: EntityLink[_LinkedEntity1T],
    entity_link2: EntityLink[_LinkedEntity2T],
    *,
    allow_archived: bool = False
) -> tuple[_EntityT, Iterable[_LinkedEntity1T], Iterable[_LinkedEntity2T]]:
    pass


async def generic_finder(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: EntityLink[_LinkedEntity1T] | None = None,
    entity_link2: EntityLink[_LinkedEntity2T] | None = None,
    *,
    allow_archived: bool = False
) -> (
    _EntityT
    | tuple[_EntityT, Iterable[_LinkedEntity1T]]
    | tuple[_EntityT, Iterable[_LinkedEntity1T], Iterable[_LinkedEntity2T]]
):
    """Load an entity and linked entities."""
    entity = await uow.get_for(entity_type).load_by_id(
        ref_id, allow_archived=allow_archived
    )

    if entity_link1 is not None:
        first_linked_entities = await uow.get_for(
            entity_link1.the_type
        ).find_all_generic(
            parent_ref_id=None,
            allow_archived=allow_archived,
            **entity_link1.get_for_entity(entity)
        )

        if entity_link2 is not None:
            second_linked_entities = await uow.get_for(
                entity_link2.the_type
            ).find_all_generic(
                parent_ref_id=None,
                allow_archived=allow_archived,
                **entity_link2.get_for_entity(entity)
            )
            return (entity, first_linked_entities, second_linked_entities)

        return (entity, first_linked_entities)
    else:
        return entity
