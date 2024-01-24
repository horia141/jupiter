"""UseCase for updating the metric collection project."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectUseCase,
)


class MetricChangeCollectionProject(
    LoggedInMutationCommand[MetricChangeCollectionProjectUseCase]
):
    """Use case for updating the metric collection project."""
