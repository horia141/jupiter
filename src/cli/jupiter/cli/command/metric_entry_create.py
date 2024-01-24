"""UseCase for creating a metric entry."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.entry.create import (
    MetricEntryCreateUseCase,
)


class MetricEntryCreate(LoggedInMutationCommand[MetricEntryCreateUseCase]):
    """UseCase for creating a metric entry."""
