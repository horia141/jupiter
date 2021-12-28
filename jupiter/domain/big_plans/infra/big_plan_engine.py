"""A unit of work for big plans."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.framework.storage import UnitOfWork, Engine


class BigPlanUnitOfWork(UnitOfWork, abc.ABC):
    """A big plans specialised unit of work."""

    @property
    @abc.abstractmethod
    def big_plan_collection_repository(self) -> BigPlanCollectionRepository:
        """The big plan collection repository."""

    @property
    @abc.abstractmethod
    def big_plan_repository(self) -> BigPlanRepository:
        """The big plan repository."""


class BigPlanEngine(Engine[BigPlanUnitOfWork], abc.ABC):
    """The big plan engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[BigPlanUnitOfWork]:
        """Build a unit of work."""
