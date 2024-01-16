from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import EntityLinkFiltersCompiled
from jupiter.core.framework.value import AtomicValue, EnumValue
from sqlalchemy import Table, select


def compile_query_relative_to(
    query_stmt: select, table: Table, filters: EntityLinkFiltersCompiled
) -> select:
    """Compile filters relative to a table."""
    for key, value in filters.items():
        if isinstance(value, EnumValue):
            query_stmt = query_stmt.where(
                table.c[key] == value.value,
            )
        elif isinstance(value, EntityId):
            query_stmt = query_stmt.where(
                table.c[key] == value.as_int(),
            )
        elif isinstance(value, AtomicValue):
            query_stmt = query_stmt.where(
                getattr(table.c, key) == value.to_primitive(),
            )
        elif isinstance(value, list):
            if len(value) == 0:
                raise Exception("Invalid type of filter")
            if not isinstance(value[0], EntityId):
                raise Exception("Invalid type of filter")
            query_stmt = query_stmt.where(
                getattr(table.c, key).in_([ref_id.as_int() for ref_id in value]),
            )
        else:
            raise Exception("Invalid type of filter")
    return query_stmt