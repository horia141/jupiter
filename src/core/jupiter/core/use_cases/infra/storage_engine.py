"""Use case specific storage interactions."""

import abc
from contextlib import AbstractAsyncContextManager

from jupiter.core.use_cases.infra.mutation_use_case_invocation_record_repository import (
    MutationUseCaseInvocationRecordRepository,
)


class UseCaseUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def mutation_use_case_invocation_record_repository(
        self,
    ) -> MutationUseCaseInvocationRecordRepository:
        """The mutation use case invocation record repository."""


class UseCaseStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AbstractAsyncContextManager[UseCaseUnitOfWork]:
        """Build a unit of work."""
