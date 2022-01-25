"""A mutation use case recoder which persists the records to storage."""
from typing import Final

from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgs, MutationUseCaseInvocationRecord
from jupiter.use_cases.infra.storage_engine import UseCaseStorageEngine


class PersistentMutationUseCaseInvocationRecorder(MutationUseCaseInvocationRecorder):
    """A mutation use case recoder which persists the records to storage."""

    _storage_engine: Final[UseCaseStorageEngine]

    def __init__(self, storage_engine: UseCaseStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def record(self, invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs]) -> None:
        """Record the invocation of the use case."""
        with self._storage_engine.get_unit_of_work() as uow:
            uow.mutation_use_case_invocation_record_repository.create(invocation_record)
