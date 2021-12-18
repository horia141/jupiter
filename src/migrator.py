"""A temporary migrator."""
import logging

from repository.yaml.inbox_tasks import YamlInboxTaskRepository
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    inbox_tasks_repository = YamlInboxTaskRepository(time_provider)
    all_inbox_tasks = inbox_tasks_repository.find_all(allow_archived=True)
    inbox_tasks_repository.dump_all(all_inbox_tasks)


if __name__ == "__main__":
    main()
