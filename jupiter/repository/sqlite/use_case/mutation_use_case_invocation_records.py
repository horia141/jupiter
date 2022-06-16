"""SQlite based repository for the invocation record of mutation use cases."""
from typing import Final

from sqlalchemy import (
    insert,
    MetaData,
    Table,
    Column,
    DateTime,
    String,
    delete,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.engine import Connection

from jupiter.framework.use_case import MutationUseCaseInvocationRecord, UseCaseArgs
from jupiter.use_cases.infra.mutation_use_case_invocation_record_repository import (
    MutationUseCaseInvocationRecordRepository,
)


class SqliteMutationUseCaseInvocationRecordRepository(
    MutationUseCaseInvocationRecordRepository
):
    """A SQlite repository for mutation use cases invocation records."""

    _connection: Final[Connection]
    _mutation_use_case_invocation_record_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._mutation_use_case_invocation_record_table = Table(
            "use_case_mutation_use_case_invocation_record",
            metadata,
            Column(
                "owner_ref_id",
                Integer,
                ForeignKey("workspace.ref_id"),
                primary_key=True,
            ),
            Column("timestamp", DateTime, primary_key=True),
            Column("name", String, primary_key=True),
            Column("args", JSON, nullable=False),
            Column("result", String, nullable=False),
            Column("error_str", String, nullable=True),
            keep_existing=True,
        )

    def create(
        self, invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs]
    ) -> None:
        """Create a new invocation record."""
        self._connection.execute(
            insert(self._mutation_use_case_invocation_record_table).values(
                owner_ref_id=invocation_record.owner_ref_id.as_int(),
                timestamp=invocation_record.timestamp.to_db(),
                name=invocation_record.name,
                args=invocation_record.args.to_serializable_dict(),
                result=invocation_record.result.to_db(),
                error_str=invocation_record.error_str,
            )
        )

    def clear_all(self) -> None:
        """Clear all entries in the invocation record."""
        self._connection.execute(
            delete(self._mutation_use_case_invocation_record_table)
        )
