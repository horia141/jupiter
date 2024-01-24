"""UseCase for updating a metric's properties."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.update import MetricUpdateUseCase


class MetricUpdate(LoggedInMutationCommand[MetricUpdateUseCase]):
    """UseCase for updating a metric's properties."""
