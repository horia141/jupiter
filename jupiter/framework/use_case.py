"""Framework level elements for use cases."""
import abc
import enum
import logging
from dataclasses import dataclass, fields
from typing import TypeVar, Generic, Final, Optional, Union

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.json import process_primitive_to_json, JSONDictType
from jupiter.framework.update_action import UpdateAction
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class UseCaseIOBase:
    """The base class for use case inputs and output types."""

    def to_serializable_dict(self) -> JSONDictType:
        """Transform this argument set to a JSON compatible representation."""
        serialized_form = {}
        for field in fields(self):
            field_value = getattr(self, field.name)
            if isinstance(field_value, UpdateAction):
                if field_value.should_change:
                    serialized_form[field.name] = process_primitive_to_json(field_value.value, field.name)
            else:
                serialized_form[field.name] = process_primitive_to_json(field_value, field.name)
        return serialized_form


class UseCaseContextBase(abc.ABC):
    """The base class for use case contexts."""

    @property
    @abc.abstractmethod
    def owner_ref_id(self) -> EntityId:
        """The owner entity root id."""


@dataclass(frozen=True)
class UseCaseArgsBase(UseCaseIOBase):
    """The base class for use case args types."""


@dataclass(frozen=True)
class UseCaseResultBase(UseCaseIOBase):
    """The base class for use case args results."""


UseCaseContext = TypeVar('UseCaseContext', bound=Union[None, UseCaseContextBase])
UseCaseArgs = TypeVar('UseCaseArgs', bound=UseCaseArgsBase)
UseCaseResult = TypeVar('UseCaseResult', bound=Union[None, UseCaseResultBase])


@enum.unique
class MutationUseCaseInvocationResult(enum.Enum):
    """The result of a mutation use case invocation."""
    SUCCESS = "success"
    FAILURE = "failure"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@dataclass(frozen=True)
class MutationUseCaseInvocationRecord(Generic[UseCaseArgs]):
    """The record of a mutation use case invocation."""

    owner_ref_id: EntityId
    timestamp: Timestamp
    name: str
    args: UseCaseArgs
    result: MutationUseCaseInvocationResult
    error_str: Optional[str]

    @staticmethod
    def build_success(
            owner_ref_id: EntityId, timestamp: Timestamp, name: str,
            args: UseCaseArgs) -> 'MutationUseCaseInvocationRecord[UseCaseArgs]':
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            owner_ref_id=owner_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.SUCCESS,
            error_str=None)

    @staticmethod
    def build_failure(
            owner_ref_id: EntityId, timestamp: Timestamp, name: str,
            args: UseCaseArgs, error: Exception) -> 'MutationUseCaseInvocationRecord[UseCaseArgs]':
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            owner_ref_id=owner_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.FAILURE,
            error_str=str(error))


class MutationUseCaseInvocationRecorder(abc.ABC):
    """A special type of recorder for mutation use cases which records the outcome of a particular use case."""

    @abc.abstractmethod
    def record(self, invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs]) -> None:
        """Record the invocation of the use case."""


class UseCase(Generic[UseCaseContext, UseCaseArgs, UseCaseResult], abc.ABC):
    """A generic use case."""

    @abc.abstractmethod
    def execute(self, args: UseCaseArgs) -> UseCaseResult:
        """Execute the command's action."""

    @abc.abstractmethod
    def _build_context(self) -> UseCaseContext:
        """Construct the context for the use case."""

    @abc.abstractmethod
    def _execute(self, context: UseCaseContext, args: UseCaseArgs) -> UseCaseResult:
        """Execute the command's action."""


class MutationUseCase(
        Generic[UseCaseContext, UseCaseArgs, UseCaseResult],
        UseCase[UseCaseContext, UseCaseArgs, UseCaseResult],
        abc.ABC):
    """A command which does some sort of mutation."""

    _time_provider: Final[TimeProvider]
    _invocation_recorder: Final[MutationUseCaseInvocationRecorder]

    def __init__(self, time_provider: TimeProvider, invocation_recorder: MutationUseCaseInvocationRecorder) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._invocation_recorder = invocation_recorder

    def execute(self, args: UseCaseArgs) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(f"Invoking mutation command {self.__class__.__name__} with args {args}")
        context = self._build_context()
        try:
            result = self._execute(context, args)
            invocation_record = \
                MutationUseCaseInvocationRecord.build_success(
                    context.owner_ref_id, self._time_provider.get_current_time(), self.__class__.__name__, args)
            self._invocation_recorder.record(invocation_record)
            return result
        except InputValidationError:
            raise
        except Exception as err:
            invocation_record = \
                MutationUseCaseInvocationRecord.build_failure(
                    context.owner_ref_id, self._time_provider.get_current_time(), self.__class__.__name__, args, err)
            self._invocation_recorder.record(invocation_record)
            raise


class ReadonlyUseCase(
        Generic[UseCaseContext, UseCaseArgs, UseCaseResult],
        UseCase[UseCaseContext, UseCaseArgs, UseCaseResult],
        abc.ABC):
    """A command which only does reads."""

    def execute(self, args: UseCaseArgs) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(f"Invoking readonly command {self.__class__.__name__} with args {args}")
        context = self._build_context()
        return self._execute(context, args)
