"""UseCase for creating a metric."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.metrics.create import MetricCreateUseCase


class MetricCreate(LoggedInMutationCommand[MetricCreateUseCase]):
    """UseCase for creating a metric."""
