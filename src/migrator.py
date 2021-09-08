"""A temporary migrator."""
import logging

from repository.inbox_tasks import InboxTasksRepository
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    inbox_tasks_repository = InboxTasksRepository(time_provider)
    all_inbox_tasks = inbox_tasks_repository.find_all_inbox_tasks(allow_archived=True)
    inbox_tasks_repository.save_all(all_inbox_tasks)


if __name__ == "__main__":
    main()
