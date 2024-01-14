"""The Slack tasks repositories."""

from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.realm import RealmCodecRegistry
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


class SqliteSlackTaskCollectionRepository(
    SqliteTrunkEntityRepository[SlackTaskCollection], SlackTaskCollectionRepository
):
    """The slack task collection repository."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            Table(
                "slack_task_collection",
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

    def _entity_to_row(self, entity: SlackTaskCollection) -> RowType:
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

    def _row_to_entity(self, row: RowType) -> SlackTaskCollection:
        return SlackTaskCollection(
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


class SqliteSlackTaskRepository(
    SqliteLeafEntityRepository[SlackTask], SlackTaskRepository
):
    """The slack task repository."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            Table(
                "slack_task",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "slack_task_collection_ref_id",
                    Integer,
                    ForeignKey("slack_task_collection.ref_id"),
                    nullable=False,
                ),
                Column("user", String(), nullable=False),
                Column("channel", String(), nullable=True),
                Column("message", String(), nullable=False),
                Column("generation_extra_info", String(), nullable=False),
                Column("has_generated_task", Boolean, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: SlackTask) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "slack_task_collection_ref_id": entity.slack_task_collection.as_int(),
            "user": str(entity.user),
            "channel": str(entity.channel) if entity.channel else None,
            "message": entity.message,
            "generation_extra_info": entity.generation_extra_info.to_db(),
            "has_generated_task": entity.has_generated_task,
        }

    def _row_to_entity(self, row: RowType) -> SlackTask:
        return SlackTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=SlackTask.build_name(
                SlackUserName.from_raw(row["user"]),
                SlackChannelName.from_raw(row["channel"]) if row["channel"] else None,
            ),
            slack_task_collection=ParentLink(
                EntityId.from_raw(
                    str(row["slack_task_collection_ref_id"]),
                )
            ),
            user=SlackUserName.from_raw(row["user"]),
            channel=SlackChannelName.from_raw(row["channel"])
            if row["channel"]
            else None,
            message=row["message"],
            generation_extra_info=PushGenerationExtraInfo.from_db(
                row["generation_extra_info"],
            ),
            has_generated_task=row["has_generated_task"],
        )
