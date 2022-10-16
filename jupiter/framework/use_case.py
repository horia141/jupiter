"""Framework level elements for use cases."""
import abc
import enum
import logging
from dataclasses import dataclass, fields
from typing import TypeVar, Generic, Final, Optional, Union, ContextManager

from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.json import process_primitive_to_json, JSONDictType
from jupiter.framework.update_action import UpdateAction
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class UseCaseContextBase(abc.ABC):
    """The base class for use case contexts."""

    @property
    @abc.abstractmethod
    def owner_ref_id(self) -> EntityId:
        """The owner entity root id."""


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
                    serialized_form[field.name] = process_primitive_to_json(
                        field_value.value, field.name
                    )
            else:
                serialized_form[field.name] = process_primitive_to_json(
                    field_value, field.name
                )
        return serialized_form


@dataclass(frozen=True)
class UseCaseArgsBase(UseCaseIOBase):
    """The base class for use case args types."""


@dataclass(frozen=True)
class UseCaseResultBase(UseCaseIOBase):
    """The base class for use case args results."""


UseCaseContext = TypeVar("UseCaseContext", bound=UseCaseContextBase)
UseCaseArgs = TypeVar("UseCaseArgs", bound=UseCaseArgsBase)
UseCaseResult = TypeVar("UseCaseResult", bound=Union[None, UseCaseResultBase])


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
        owner_ref_id: EntityId, timestamp: Timestamp, name: str, args: UseCaseArgs
    ) -> "MutationUseCaseInvocationRecord[UseCaseArgs]":
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            owner_ref_id=owner_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.SUCCESS,
            error_str=None,
        )

    @staticmethod
    def build_failure(
        owner_ref_id: EntityId,
        timestamp: Timestamp,
        name: str,
        args: UseCaseArgs,
        error: Exception,
    ) -> "MutationUseCaseInvocationRecord[UseCaseArgs]":
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            owner_ref_id=owner_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.FAILURE,
            error_str=str(error),
        )


class MutationUseCaseInvocationRecorder(abc.ABC):
    """A special type of recorder for mutation use cases which records the outcome of a particular use case."""

    @abc.abstractmethod
    def record(
        self, invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs]
    ) -> None:
        """Record the invocation of the use case."""


@enum.unique
class MarkProgressStatus(enum.Enum):
    """The status of a big plan."""

    PROGRESS = "progress"
    OK = "ok"
    FAILED = "failed"
    NOT_NEEDED = "not-needed"


class EntityProgressReporter(abc.ABC):
    """A reporter for the updates to a particular entity."""

    @abc.abstractmethod
    def mark_not_needed(self) -> "EntityProgressReporter":
        """Mark the fact that a particular modification isn't needed."""

    @abc.abstractmethod
    def mark_known_entity_id(self, entity_id: EntityId) -> "EntityProgressReporter":
        """Mark the fact that we now know the entity id for the entity being processed."""

    @abc.abstractmethod
    def mark_known_name(self, name: str) -> "EntityProgressReporter":
        """Mark the fact that we now know the entity name for the entity being processed."""

    @abc.abstractmethod
    def mark_local_change(self) -> "EntityProgressReporter":
        """Mark the fact that the local change has succeeded."""

    @abc.abstractmethod
    def mark_remote_change(
        self, success: MarkProgressStatus = MarkProgressStatus.OK
    ) -> "EntityProgressReporter":
        """Mark the fact that the remote change has completed."""

    @abc.abstractmethod
    def mark_other_progress(
        self, progress: str, success: MarkProgressStatus = MarkProgressStatus.OK
    ) -> "EntityProgressReporter":
        """Mark some other type of progress."""


class ProgressReporter(abc.ABC):
    """A reporter to the user in real-time on modifications to entities."""

    @abc.abstractmethod
    def section(self, title: str) -> ContextManager[None]:
        """Start a section or subsection."""

    @abc.abstractmethod
    def start_creating_entity(
        self, entity_type: str, entity_name: str
    ) -> ContextManager[EntityProgressReporter]:
        """Report that a particular entity is being created."""

    @abc.abstractmethod
    def start_updating_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> ContextManager[EntityProgressReporter]:
        """Report that a particular entity is being updated."""

    @abc.abstractmethod
    def start_archiving_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> ContextManager[EntityProgressReporter]:
        """Report that a particular entity is being archived."""

    @abc.abstractmethod
    def start_removing_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> ContextManager[EntityProgressReporter]:
        """Report that a particular entity is being removed."""

    @abc.abstractmethod
    def start_work_related_to_entity(
        self, entity_type: str, entity_id: EntityId, entity_name: str
    ) -> ContextManager[EntityProgressReporter]:
        """Report that a particular entity is being affected."""

    @abc.abstractmethod
    def start_complex_entity_work(
        self, entity_type: str, entity_id: EntityId, entity_name: str
    ) -> ContextManager["ProgressReporter"]:
        """Create a progress reporter with some scoping to operate with subentities of a main entity."""


class UseCase(Generic[UseCaseContext, UseCaseArgs, UseCaseResult], abc.ABC):
    """A generic use case."""

    @abc.abstractmethod
    def execute(
        self, progress_reporter: ProgressReporter, args: UseCaseArgs
    ) -> UseCaseResult:
        """Execute the command's action."""

    @abc.abstractmethod
    def _build_context(self) -> UseCaseContext:
        """Construct the context for the use case."""

    @abc.abstractmethod
    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: UseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


@dataclass(frozen=True)
class EmptyContext(UseCaseContextBase):
    """An empty context."""

    @property
    def owner_ref_id(self) -> EntityId:
        """The owner root entity id."""
        return BAD_REF_ID


class MutationEmptyContextUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    UseCase[EmptyContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation, but cannot rely on a context."""

    def _build_context(self) -> EmptyContext:
        """Construct the context for the use case."""
        return EmptyContext()

    def execute(
        self, progress_reporter: ProgressReporter, args: UseCaseArgs
    ) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(
            f"Invoking no-context mutation command {self.__class__.__name__} with args {args}"
        )
        return self._execute(progress_reporter, EmptyContext(), args)


class MutationUseCase(
    Generic[UseCaseContext, UseCaseArgs, UseCaseResult],
    UseCase[UseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation."""

    _time_provider: Final[TimeProvider]
    _invocation_recorder: Final[MutationUseCaseInvocationRecorder]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
    ) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._invocation_recorder = invocation_recorder

    def execute(
        self, progress_reporter: ProgressReporter, args: UseCaseArgs
    ) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(
            f"Invoking mutation command {self.__class__.__name__} with args {args}"
        )
        context = self._build_context()

        try:
            result = self._execute(progress_reporter, context, args)
        except InputValidationError:
            raise
        except Exception as err:
            invocation_record = MutationUseCaseInvocationRecord.build_failure(
                context.owner_ref_id if context else BAD_REF_ID,
                self._time_provider.get_current_time(),
                self.__class__.__name__,
                args,
                err,
            )
            self._invocation_recorder.record(invocation_record)
            raise

        invocation_record = MutationUseCaseInvocationRecord.build_success(
            context.owner_ref_id if context is not None else BAD_REF_ID,
            self._time_provider.get_current_time(),
            self.__class__.__name__,
            args,
        )
        self._invocation_recorder.record(invocation_record)
        return result


class ReadonlyUseCase(
    Generic[UseCaseContext, UseCaseArgs, UseCaseResult],
    UseCase[UseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which only does reads."""

    def execute(
        self, progress_reporter: ProgressReporter, args: UseCaseArgs
    ) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(
            f"Invoking readonly command {self.__class__.__name__} with args {args}"
        )
        context = self._build_context()
        return self._execute(progress_reporter, context, args)
