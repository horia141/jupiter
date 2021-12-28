"""Framework level elements for use cases."""
import abc
from typing import TypeVar, Generic


UseCaseArgs = TypeVar('UseCaseArgs')
UseCaseResult = TypeVar('UseCaseResult')


class UseCase(Generic[UseCaseArgs, UseCaseResult], abc.ABC):
    """A command."""

    @abc.abstractmethod
    def execute(self, args: UseCaseArgs) -> UseCaseResult:
        """Execute the command's action."""
