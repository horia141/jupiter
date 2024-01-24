"""UseCase for archiving a metric entry."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.entry.archive import (
    MetricEntryArchiveUseCase,
)


class MetricEntryArchive(LoggedInMutationCommand[MetricEntryArchiveUseCase]):
    """UseCase for archiving a metric entry."""
