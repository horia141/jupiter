"""A repository for task generation logs."""
import abc

from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class GenLogRepository(TrunkEntityRepository[GenLog], abc.ABC):
    """A repository of task generation logs."""
