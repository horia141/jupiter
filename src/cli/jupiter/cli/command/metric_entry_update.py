"""UseCase for updating a metric entry's properties."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.entry.update import (
    MetricEntryUpdateUseCase,
)


class MetricEntryUpdate(LoggedInMutationCommand[MetricEntryUpdateUseCase]):
    """UseCase for updating a metric entry's properties."""
