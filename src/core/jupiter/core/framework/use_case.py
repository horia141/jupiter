"""Framework level elements for use cases."""
import abc
import enum
import logging
from dataclasses import dataclass, fields
from typing import AsyncContextManager, Final, Generic, Optional, TypeVar, Union

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.json import JSONDictType, process_primitive_to_json
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class UseCaseSessionBase:
    """The base class for use case sessions."""


class UseCaseContextBase(abc.ABC):
    """The base class for use case contexts."""

    @property
    @abc.abstractmethod
    def user_ref_id(self) -> EntityId:
        """The owner user id."""

    @property
    @abc.abstractmethod
    def workspace_ref_id(self) -> EntityId:
        """The owner workspace id."""


@dataclass
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
                        field_value.just_the_value,
                        field.name,
                    )
            else:
                serialized_form[field.name] = process_primitive_to_json(
                    field_value,
                    field.name,
                )
        return serialized_form


@dataclass
class UseCaseArgsBase(UseCaseIOBase):
    """The base class for use case args types."""


@dataclass
class UseCaseResultBase(UseCaseIOBase):
    """The base class for use case args results."""


UseCaseSession = TypeVar("UseCaseSession", bound=UseCaseSessionBase)
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


@dataclass
class MutationUseCaseInvocationRecord(Generic[UseCaseArgs]):
    """The record of a mutation use case invocation."""

    user_ref_id: EntityId
    workspace_ref_id: EntityId
    timestamp: Timestamp
    name: str
    args: UseCaseArgs
    result: MutationUseCaseInvocationResult
    error_str: Optional[str]

    @staticmethod
    def build_success(
        user_ref_id: EntityId,
        workspace_ref_id: EntityId,
        timestamp: Timestamp,
        name: str,
        args: UseCaseArgs,
    ) -> "MutationUseCaseInvocationRecord[UseCaseArgs]":
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            user_ref_id=user_ref_id,
            workspace_ref_id=workspace_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.SUCCESS,
            error_str=None,
        )

    @staticmethod
    def build_failure(
        user_ref_id: EntityId,
        workspace_ref_id: EntityId,
        timestamp: Timestamp,
        name: str,
        args: UseCaseArgs,
        error: Exception,
    ) -> "MutationUseCaseInvocationRecord[UseCaseArgs]":
        """Build a success case for an invocation."""
        return MutationUseCaseInvocationRecord(
            user_ref_id=user_ref_id,
            workspace_ref_id=workspace_ref_id,
            timestamp=timestamp,
            name=name,
            args=args,
            result=MutationUseCaseInvocationResult.FAILURE,
            error_str=str(error),
        )


class MutationUseCaseInvocationRecorder(abc.ABC):
    """A special type of recorder for mutation use cases which records the outcome of a particular use case."""

    @abc.abstractmethod
    async def record(
        self,
        invocation_record: MutationUseCaseInvocationRecord[UseCaseArgs],
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
    async def mark_not_needed(self) -> "EntityProgressReporter":
        """Mark the fact that a particular modification isn't needed."""

    @abc.abstractmethod
    async def mark_known_entity_id(
        self,
        entity_id: EntityId,
    ) -> "EntityProgressReporter":
        """Mark the fact that we now know the entity id for the entity being processed."""

    @abc.abstractmethod
    async def mark_known_name(self, name: str) -> "EntityProgressReporter":
        """Mark the fact that we now know the entity name for the entity being processed."""

    @abc.abstractmethod
    async def mark_local_change(self) -> "EntityProgressReporter":
        """Mark the fact that the local change has succeeded."""

    @abc.abstractmethod
    async def mark_remote_change(
        self,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> "EntityProgressReporter":
        """Mark the fact that the remote change has completed."""

    @abc.abstractmethod
    async def mark_other_progress(
        self,
        progress: str,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> "EntityProgressReporter":
        """Mark some other type of progress."""


class ContextProgressReporter(abc.ABC):
    """A reporter to the user in real-time on modifications to entities."""

    @abc.abstractmethod
    def section(self, title: str) -> AsyncContextManager[None]:
        """Start a section or subsection."""

    @abc.abstractmethod
    def start_creating_entity(
        self,
        entity_type: str,
        entity_name: str,
    ) -> AsyncContextManager[EntityProgressReporter]:
        """Report that a particular entity is being created."""

    @abc.abstractmethod
    def start_updating_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncContextManager[EntityProgressReporter]:
        """Report that a particular entity is being updated."""

    @abc.abstractmethod
    def start_archiving_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncContextManager[EntityProgressReporter]:
        """Report that a particular entity is being archived."""

    @abc.abstractmethod
    def start_removing_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncContextManager[EntityProgressReporter]:
        """Report that a particular entity is being removed."""

    @abc.abstractmethod
    def start_complex_entity_work(
        self,
        entity_type: str,
        entity_id: EntityId,
        entity_name: str,
    ) -> AsyncContextManager["ContextProgressReporter"]:
        """Create a progress reporter with some scoping to operate with subentities of a main entity."""


class ProgressReporterFactory(Generic[UseCaseContext], abc.ABC):
    """A factory for progress reporters."""

    @abc.abstractmethod
    def new_reporter(self, context: UseCaseContext) -> ContextProgressReporter:
        """Build a progress reporter for a given context."""


class UseCase(
    Generic[UseCaseSession, UseCaseContext, UseCaseArgs, UseCaseResult], abc.ABC
):
    """A generic use case."""

    @abc.abstractmethod
    async def execute(
        self,
        session: UseCaseSession,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""

    @abc.abstractmethod
    async def _build_context(self, session: UseCaseSession) -> UseCaseContext:
        """Construct the context for the use case."""


@dataclass
class EmptySession(UseCaseSessionBase):
    """An empty session."""


@dataclass
class EmptyContext(UseCaseContextBase):
    """An empty context."""

    @property
    def user_ref_id(self) -> EntityId:
        """The user context."""
        return BAD_REF_ID

    @property
    def workspace_ref_id(self) -> EntityId:
        """The owner root entity id."""
        return BAD_REF_ID


class MutationUseCase(
    Generic[UseCaseSession, UseCaseContext, UseCaseArgs, UseCaseResult],
    UseCase[UseCaseSession, UseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation."""

    _time_provider: Final[TimeProvider]
    _invocation_recorder: Final[MutationUseCaseInvocationRecorder]
    _progress_reporter_factory: ProgressReporterFactory[UseCaseContext]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[UseCaseContext],
    ) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._invocation_recorder = invocation_recorder
        self._progress_reporter_factory = progress_reporter_factory

    async def execute(
        self,
        session: UseCaseSession,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(
            f"Invoking mutation command {self.__class__.__name__} with args {args}",
        )
        context = await self._build_context(session)
        progress_reporter = self._progress_reporter_factory.new_reporter(context)

        try:
            result = await self._execute(progress_reporter, context, args)
        except InputValidationError:
            raise
        except Exception as err:
            invocation_record = MutationUseCaseInvocationRecord.build_failure(
                user_ref_id=context.user_ref_id,
                workspace_ref_id=context.workspace_ref_id,
                timestamp=self._time_provider.get_current_time(),
                name=self.__class__.__name__,
                args=args,
                error=err,
            )
            try:
                await self._invocation_recorder.record(invocation_record)
            except:  # noqa: E722
                LOGGER.critical("Error writing invocation record")
            raise

        user_ref_id = context.user_ref_id
        workspace_ref_id = context.workspace_ref_id
        if self.__class__.__name__ == "InitUseCase":
            # HACK HACK HACK HACK!
            # We're dealing with an init result, so we need to do some adjustments
            # to the context owner
            user_ref_id = result.new_user.ref_id  # type: ignore
            workspace_ref_id = result.new_workspace.ref_id  # type: ignore

        invocation_record = MutationUseCaseInvocationRecord.build_success(
            user_ref_id=user_ref_id,
            workspace_ref_id=workspace_ref_id,
            timestamp=self._time_provider.get_current_time(),
            name=self.__class__.__name__,
            args=args,
        )
        await self._invocation_recorder.record(invocation_record)
        return result

    @abc.abstractmethod
    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: UseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


class ReadonlyUseCase(
    Generic[UseCaseSession, UseCaseContext, UseCaseArgs, UseCaseResult],
    UseCase[UseCaseSession, UseCaseContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which only does reads."""

    async def execute(
        self,
        session: UseCaseSession,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        LOGGER.info(
            f"Invoking readonly command {self.__class__.__name__} with args {args}",
        )
        context = await self._build_context(session)
        return await self._execute(context, args)

    @abc.abstractmethod
    async def _execute(
        self,
        context: UseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""