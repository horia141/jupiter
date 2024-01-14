"""The Email tasks repositories."""

from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskRepository,
)
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteEmailTaskCollectionRepository(
    SqliteTrunkEntityRepository[EmailTaskCollection], EmailTaskCollectionRepository
):
    """The email task collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "email_task_collection",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "push_integration_group_ref_id",
                    Integer,
                    ForeignKey("push_integration_group_ref_id.ref_id"),
                    unique=True,
                    index=True,
                    nullable=False,
                ),
                Column(
                    "generation_project_ref_id",
                    Integer,
                    ForeignKey("project.ref_id"),
                    nullable=False,
                ),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: EmailTaskCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "push_integration_group_ref_id": entity.push_integration_group.as_int(),
            "generation_project_ref_id": entity.generation_project_ref_id.as_int(),
        }

    def _row_to_entity(self, row: RowType) -> EmailTaskCollection:
        return EmailTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            push_integration_group=ParentLink(
                EntityId.from_raw(
                    str(row["push_integration_group_ref_id"]),
                )
            ),
            generation_project_ref_id=EntityId.from_raw(
                str(row["generation_project_ref_id"]),
            ),
        )


class SqliteEmailTaskRepository(
    SqliteLeafEntityRepository[EmailTask], EmailTaskRepository
):
    """The email task repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "email_task",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "email_task_collection_ref_id",
                    Integer,
                    ForeignKey("email_task_collection.ref_id"),
                    nullable=False,
                ),
                Column("from_address", String(), nullable=False),
                Column("from_name", String(), nullable=False),
                Column("to_address", String(), nullable=False),
                Column("subject", String(), nullable=False),
                Column("body", String(), nullable=False),
                Column("generation_extra_info", String(), nullable=False),
                Column("has_generated_task", Boolean, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: EmailTask) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "email_task_collection_ref_id": entity.email_task_collection.as_int(),
            "from_address": str(entity.from_address),
            "from_name": str(entity.from_name),
            "to_address": str(entity.to_address),
            "subject": entity.subject,
            "body": entity.body,
            "generation_extra_info": entity.generation_extra_info.to_db(),
            "has_generated_task": entity.has_generated_task,
        }

    def _row_to_entity(self, row: RowType) -> EmailTask:
        return EmailTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=EmailTask.build_name(
                EmailAddress.from_raw(row["from_address"]),
                EmailUserName.from_raw(row["from_name"]),
                row["subject"],
            ),
            email_task_collection=ParentLink(
                EntityId.from_raw(
                    str(row["email_task_collection_ref_id"]),
                )
            ),
            from_address=EmailAddress.from_raw(row["from_address"]),
            from_name=EmailUserName.from_raw(row["from_name"]),
            to_address=EmailAddress.from_raw(row["to_address"]),
            subject=row["subject"],
            body=row["body"],
            generation_extra_info=PushGenerationExtraInfo.from_db(
                row["generation_extra_info"],
            ),
            has_generated_task=row["has_generated_task"],
        )
