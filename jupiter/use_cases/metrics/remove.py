"""The command for hard removing a metric."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.metrics.infra.metric_engine import MetricEngine
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricRemoveUseCase(UseCase[MetricKey, None]):
    """The command for removing a metric."""

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _metric_notion_manager: Final[MetricNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
                 inbox_task_notion_manager: InboxTaskNotionManager, metric_engine: MetricEngine,
                 metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._metric_notion_manager = metric_notion_manager
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: MetricKey) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.load_by_key(args)

        MetricRemoveService(self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager,
                            self._metric_engine, self._metric_notion_manager).execute(metric)
