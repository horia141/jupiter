"""SQlite based repository for the invocation record of mutation use cases."""
from typing import Final
from jupiter.core.framework.realm import DatabaseRealm, RealmCodecRegistry

from jupiter.core.framework.use_case import MutationUseCaseInvocationRecord, UseCaseArgs
from jupiter.core.use_cases.infra.mutation_use_case_invocation_record_repository import (
    MutationUseCaseInvocationRecordRepository,
)
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteMutationUseCaseInvocationRecordRepository(
    MutationUseCaseInvocationRecordRepository,
):
    """A SQlite repository for mutation use cases invocation records."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _connection: Final[AsyncConnection]
    _mutation_use_case_invocation_record_table: Final[Table]

    def __init__(self, realm_codec_registry: RealmCodecRegistry, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._connection = connection
        self._mutation_use_case_invocation_record_table = Table(
            "use_case_mutation_use_case_invocation_record",
            metadata,
            Column("user_ref_id", Integer, ForeignKey("user.ref_id"), primary_key=True),
            Column(
                "workspace_ref_id",
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

    async def create(
        self,
        invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs],
    ) -> None:
        """Create a new invocation record."""
        args_encoder = self._realm_codec_registry.get_encoder(invocation_record.args.__class__, DatabaseRealm)
        await self._connection.execute(
            insert(self._mutation_use_case_invocation_record_table).values(
                user_ref_id=invocation_record.user_ref_id.as_int(),
                workspace_ref_id=invocation_record.workspace_ref_id.as_int(),
                timestamp=invocation_record.timestamp.to_db(),
                name=invocation_record.name,
                args=args_encoder.encode(invocation_record.args),
                result=invocation_record.result.to_db(),
                error_str=invocation_record.error_str,
            ),
        )

    async def clear_all(self) -> None:
        """Clear all entries in the invocation record."""
        await self._connection.execute(
            delete(self._mutation_use_case_invocation_record_table),
        )
