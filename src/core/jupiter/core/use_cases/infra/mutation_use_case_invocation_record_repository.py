"""A repository for mutation use cases invocation records."""
import abc

from jupiter.core.framework.repository import Repository
from jupiter.core.framework.use_case import MutationUseCaseInvocationRecord, UseCaseArgs


class MutationUseCaseInvocationRecordRepository(Repository, abc.ABC):
    """A repository for mutation use cases invocation records."""

    @abc.abstractmethod
    async def create(
        self,
        invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs],
    ) -> None:
        """Create a new invocation record."""

    @abc.abstractmethod
    async def clear_all(self) -> None:
        """Clear all invocation record entries."""
