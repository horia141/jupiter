"""A temporary migrator."""
import logging

import coloredlogs

from jupiter.repository.yaml.inbox_tasks import YamlInboxTaskRepository
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    coloredlogs.install(
        level=logging.INFO,
        fmt="%(asctime)s %(name)-12s %(levelname)-6s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    time_provider = TimeProvider()

    repository = YamlInboxTaskRepository(time_provider)
    entities = repository.find_all(allow_archived=True)
    repository.dump_all(entities)


if __name__ == "__main__":
    main()
