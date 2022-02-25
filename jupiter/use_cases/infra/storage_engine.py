"""Use case specific storage interactions."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.use_cases.infra.mutation_use_case_invocation_record_repository import \
    MutationUseCaseInvocationRecordRepository


class UseCaseUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def mutation_use_case_invocation_record_repository(self) -> MutationUseCaseInvocationRecordRepository:
        """The mutation use case invocation record repository."""


class UseCaseStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[UseCaseUnitOfWork]:
        """Build a unit of work."""
