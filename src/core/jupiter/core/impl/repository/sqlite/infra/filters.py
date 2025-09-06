"""This module contains the implementation of the filters for the SQLite repository."""

from jupiter.core.framework.entity import EntityLinkFiltersCompiled, NoFilter
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import DatabaseRealm, RealmCodecRegistry
from jupiter.core.framework.utils import is_primitive_type
from jupiter.core.framework.value import AtomicValue, EnumValue
from sqlalchemy import Select, Table


def compile_query_relative_to(
    realm_codec_registry: RealmCodecRegistry,
    query_stmt: Select[tuple[Primitive, ...]],
    table: Table,
    filters: EntityLinkFiltersCompiled,
) -> Select[tuple[Primitive, ...]]:
    """Compile filters relative to a table."""
    for key, value in filters.items():
        if isinstance(value, NoFilter):
            continue
        elif is_primitive_type(value.__class__):
            query_stmt = query_stmt.where(
                getattr(table.c, key) == value,
            )
        elif isinstance(value, (AtomicValue, EnumValue)):
            encoder = realm_codec_registry.get_encoder(value.__class__, DatabaseRealm)
            query_stmt = query_stmt.where(
                getattr(table.c, key) == encoder.encode(value),
            )
        elif isinstance(value, list):
            if len(value) == 0:
                query_stmt = query_stmt.where(False)
            else:
                query_stmt = query_stmt.where(
                    getattr(table.c, key).in_(
                        [realm_codec_registry.db_encode(v, DatabaseRealm) for v in value]
                    ),
                )
        else:
            raise Exception(f"Invalid type of filter {value}")
    return query_stmt
