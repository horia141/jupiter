"""A repository for mutation use cases invocation records."""
import abc

from jupiter.framework.repository import Repository
from jupiter.framework.use_case import MutationUseCaseInvocationRecord, UseCaseArgs


class MutationUseCaseInvocationRecordRepository(Repository, abc.ABC):
    """A repository for mutation use cases invocation records."""

    @abc.abstractmethod
    def create(
        self, invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs]
    ) -> None:
        """Create a new invocation record."""
