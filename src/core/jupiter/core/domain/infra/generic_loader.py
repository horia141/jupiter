"""A generic entity loader."""
from collections.abc import Iterable
from typing import TypeVar, overload

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import (
    ContainsAtMostOne,
    ContainsMany,
    ContainsOne,
    CrownEntity,
    EntityLink,
    OwnsAtMostOne,
    OwnsMany,
    OwnsOne,
    RefsAtMostOne,
    RefsAtMostOneCond,
    RefsMany,
    RefsOne,
)
from jupiter.core.framework.repository import EntityNotFoundError

_EntityT = TypeVar("_EntityT", bound=CrownEntity)
_LinkedEntity1T = TypeVar("_LinkedEntity1T", bound=CrownEntity)
_LinkedEntity2T = TypeVar("_LinkedEntity2T", bound=CrownEntity)


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> _EntityT:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsOne[_LinkedEntity1T]
    | OwnsOne[_LinkedEntity1T]
    | RefsOne[_LinkedEntity1T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsAtMostOne[_LinkedEntity1T]
    | OwnsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOneCond[_LinkedEntity1T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T | None]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsMany[_LinkedEntity1T]
    | OwnsMany[_LinkedEntity1T]
    | RefsMany[_LinkedEntity1T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, Iterable[_LinkedEntity1T]]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsOne[_LinkedEntity1T]
    | OwnsOne[_LinkedEntity1T]
    | RefsOne[_LinkedEntity1T],
    entity_link2: ContainsOne[_LinkedEntity2T]
    | OwnsOne[_LinkedEntity2T]
    | RefsOne[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T, _LinkedEntity2T]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsOne[_LinkedEntity1T]
    | OwnsOne[_LinkedEntity1T]
    | RefsOne[_LinkedEntity1T],
    entity_link2: ContainsAtMostOne[_LinkedEntity2T]
    | OwnsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOneCond[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T, _LinkedEntity2T | None]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsOne[_LinkedEntity1T]
    | OwnsOne[_LinkedEntity1T]
    | RefsOne[_LinkedEntity1T],
    entity_link2: ContainsMany[_LinkedEntity2T]
    | OwnsMany[_LinkedEntity2T]
    | RefsMany[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T, Iterable[_LinkedEntity2T]]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsAtMostOne[_LinkedEntity1T]
    | OwnsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOneCond[_LinkedEntity1T],
    entity_link2: ContainsOne[_LinkedEntity2T]
    | OwnsOne[_LinkedEntity2T]
    | RefsOne[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T | None, _LinkedEntity2T]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsAtMostOne[_LinkedEntity1T]
    | OwnsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOneCond[_LinkedEntity1T],
    entity_link2: ContainsAtMostOne[_LinkedEntity2T]
    | OwnsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOneCond[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T | None, _LinkedEntity2T | None]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsAtMostOne[_LinkedEntity1T]
    | OwnsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOne[_LinkedEntity1T]
    | RefsAtMostOneCond[_LinkedEntity1T],
    entity_link2: ContainsMany[_LinkedEntity2T]
    | OwnsMany[_LinkedEntity2T]
    | RefsMany[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, _LinkedEntity1T | None, Iterable[_LinkedEntity2T]]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsMany[_LinkedEntity1T]
    | OwnsMany[_LinkedEntity1T]
    | RefsMany[_LinkedEntity1T],
    entity_link2: ContainsOne[_LinkedEntity2T]
    | OwnsOne[_LinkedEntity2T]
    | RefsOne[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, Iterable[_LinkedEntity1T], _LinkedEntity2T]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsMany[_LinkedEntity1T]
    | OwnsMany[_LinkedEntity1T]
    | RefsMany[_LinkedEntity1T],
    entity_link2: ContainsAtMostOne[_LinkedEntity2T]
    | OwnsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOne[_LinkedEntity2T]
    | RefsAtMostOneCond[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, Iterable[_LinkedEntity1T], _LinkedEntity2T | None]:
    """A generic entity loader."""


@overload
async def generic_loader(
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: ContainsMany[_LinkedEntity1T]
    | OwnsMany[_LinkedEntity1T]
    | RefsMany[_LinkedEntity1T],
    entity_link2: ContainsMany[_LinkedEntity2T]
    | OwnsMany[_LinkedEntity2T]
    | RefsMany[_LinkedEntity2T],
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
) -> tuple[_EntityT, Iterable[_LinkedEntity1T], Iterable[_LinkedEntity2T]]:
    """A generic entity loader."""


async def generic_loader(  # type: ignore[no-untyped-def]
    uow: DomainUnitOfWork,
    entity_type: type[_EntityT],
    ref_id: EntityId,
    entity_link1: EntityLink[_LinkedEntity1T] | None = None,
    entity_link2: EntityLink[_LinkedEntity2T] | None = None,
    *,
    allow_archived: bool = False,
    allow_subentity_archived: bool = False,
):
    """Load an entity by its ref_id."""
    entity = await uow.get_for(entity_type).load_by_id(
        ref_id, allow_archived=allow_archived
    )

    if entity_link1 is not None:
        final_first_linked_entities: _LinkedEntity1T | (None) | Iterable[
            _LinkedEntity1T
        ]

        if isinstance(
            entity_link1, RefsAtMostOneCond
        ) and not entity_link1.eval_self_cond(entity):
            final_first_linked_entities = None
        else:
            first_linked_entities = await uow.get_for(
                entity_link1.the_type
            ).find_all_generic(
                parent_ref_id=None,
                allow_archived=allow_subentity_archived,
                **entity_link1.get_for_entity(entity),
            )

            if (
                isinstance(entity_link1, ContainsOne)
                or isinstance(entity_link1, OwnsOne)
                or isinstance(entity_link1, RefsOne)
            ):
                if len(first_linked_entities) == 0:
                    raise EntityNotFoundError(f"Could not find {entity_link1.the_type}")
                elif len(first_linked_entities) >= 2:
                    raise Exception(f"Found more {entity_link1.the_type} than expected")
                final_first_linked_entities = first_linked_entities[0]
            elif (
                isinstance(entity_link1, ContainsAtMostOne)
                or isinstance(entity_link1, OwnsAtMostOne)
                or isinstance(entity_link1, RefsAtMostOne)
                or isinstance(entity_link1, RefsAtMostOneCond)
            ):
                if len(first_linked_entities) >= 2:
                    raise Exception(f"Found more {entity_link1.the_type} than expected")
                final_first_linked_entities = (
                    first_linked_entities[0] if len(first_linked_entities) > 0 else None
                )
            else:
                final_first_linked_entities = first_linked_entities

        final_second_linked_entities: _LinkedEntity2T | (None) | Iterable[
            _LinkedEntity2T
        ]

        if entity_link2 is not None:
            if isinstance(
                entity_link2, RefsAtMostOneCond
            ) and not entity_link2.eval_self_cond(entity):
                final_second_linked_entities = None
            else:
                second_linked_entities = await uow.get_for(
                    entity_link2.the_type
                ).find_all_generic(
                    parent_ref_id=None,
                    allow_archived=allow_subentity_archived,
                    **entity_link2.get_for_entity(entity),
                )

                if (
                    isinstance(entity_link2, ContainsOne)
                    or isinstance(entity_link2, OwnsOne)
                    or isinstance(entity_link2, RefsOne)
                ):
                    if len(second_linked_entities) == 0:
                        raise EntityNotFoundError(
                            f"Could not find {entity_link2.the_type}"
                        )
                    elif len(second_linked_entities) >= 2:
                        raise Exception(
                            f"Found more {entity_link2.the_type} than expected"
                        )
                    final_second_linked_entities = second_linked_entities[0]
                elif (
                    isinstance(entity_link2, ContainsAtMostOne)
                    or isinstance(entity_link2, OwnsAtMostOne)
                    or isinstance(entity_link2, RefsAtMostOne)
                    or isinstance(entity_link2, RefsAtMostOneCond)
                ):
                    if len(second_linked_entities) >= 2:
                        raise Exception(
                            f"Found more {entity_link2.the_type} than expected"
                        )
                    final_second_linked_entities = (
                        second_linked_entities[0]
                        if len(second_linked_entities) > 0
                        else None
                    )
                else:
                    final_second_linked_entities = second_linked_entities

            return (entity, final_first_linked_entities, final_second_linked_entities)

        return (entity, final_first_linked_entities)
    else:
        return entity
