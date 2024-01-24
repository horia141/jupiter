"""UseCase for hard removing a metric entry."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.entry.remove import (
    MetricEntryRemoveUseCase,
)


class MetricEntryRemove(LoggedInMutationCommand[MetricEntryRemoveUseCase]):
    """UseCase for hard removing a metric."""
