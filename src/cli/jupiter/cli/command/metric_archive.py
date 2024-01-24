"""UseCase for archiving a metric."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.archive import (
    MetricArchiveUseCase,
)


class MetricArchive(LoggedInMutationCommand[MetricArchiveUseCase]):
    """UseCase for creating a metric."""
