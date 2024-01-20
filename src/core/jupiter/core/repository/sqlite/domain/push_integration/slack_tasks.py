"""The Slack tasks repositories."""

from jupiter.core.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)


class SqliteSlackTaskCollectionRepository(
    SqliteTrunkEntityRepository[SlackTaskCollection], SlackTaskCollectionRepository
):
    """The slack task collection repository."""


class SqliteSlackTaskRepository(
    SqliteLeafEntityRepository[SlackTask], SlackTaskRepository
):
    """The slack task repository."""
