"""UseCase for removing a metric."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.remove import MetricRemoveUseCase


class MetricRemove(LoggedInMutationCommand[MetricRemoveUseCase]):
    """UseCase for hard removing a metric."""
