"""A unit of work for metrics."""
import abc
from contextlib import contextmanager
from typing import Iterator

from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_repository import MetricRepository
from models.framework import UnitOfWork, Engine


class MetricUnitOfWork(UnitOfWork, abc.ABC):
    """A metric specialized unit of work."""

    @property
    @abc.abstractmethod
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""

    @property
    @abc.abstractmethod
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""


class MetricEngine(Engine[MetricUnitOfWork], abc.ABC):
    """The metric engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[MetricUnitOfWork]:
        """Build a unit of work."""
