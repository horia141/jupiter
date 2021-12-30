"""A temporary migrator."""
import logging

from jupiter.repository.yaml.big_plans import YamlBigPlanRepository
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    repository = YamlBigPlanRepository(time_provider)
    entities = repository.find_all(allow_archived=True)
    repository.dump_all(entities)


if __name__ == "__main__":
    main()
