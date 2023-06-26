"""Module for command base class."""

import abc
from argparse import ArgumentParser, Namespace
from typing import Any, Final, Generic, TypeVar

from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestReadonlyUseCase,
    AppLoggedInMutationUseCase,
    AppLoggedInReadonlyUseCase,
)


class Command(abc.ABC):
    """The base class for command."""

    @staticmethod
    @abc.abstractmethod
    def name() -> str:
        """The name of the command."""

    @staticmethod
    @abc.abstractmethod
    def description() -> str:
        """The description of the command."""

    @abc.abstractmethod
    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    @abc.abstractmethod
    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return True

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return True


GuestMutationCommandUseCase = TypeVar(
    "GuestMutationCommandUseCase", bound=AppGuestMutationUseCase[Any, Any]
)


class GuestMutationCommand(Generic[GuestMutationCommandUseCase], Command, abc.ABC):
    """Base class for commands which do not require authentication."""

    _session_storage: Final[SessionStorage]
    _use_case: GuestMutationCommandUseCase

    def __init__(
        self, session_storage: SessionStorage, use_case: GuestMutationCommandUseCase
    ) -> None:
        """Constructor."""
        self._session_storage = session_storage
        self._use_case = use_case

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load_optional()
        await self._run(session_info, args)

    @abc.abstractmethod
    async def _run(
        self,
        session: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""


GuestReadonlyCommandUseCase = TypeVar(
    "GuestReadonlyCommandUseCase", bound=AppGuestReadonlyUseCase[Any, Any]
)


class GuestReadonlyCommand(Generic[GuestReadonlyCommandUseCase], Command, abc.ABC):
    """Base class for commands which just read and present data."""

    _session_storage: Final[SessionStorage]
    _use_case: GuestReadonlyCommandUseCase

    def __init__(
        self, session_storage: SessionStorage, use_case: GuestReadonlyCommandUseCase
    ) -> None:
        """Constructor."""
        self._session_storage = session_storage
        self._use_case = use_case

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load_optional()
        await self._run(session_info, args)

    @abc.abstractmethod
    async def _run(
        self,
        session: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False


LoggedInMutationCommandUseCase = TypeVar(
    "LoggedInMutationCommandUseCase", bound=AppLoggedInMutationUseCase[Any, Any]
)


class LoggedInMutationCommand(
    Generic[LoggedInMutationCommandUseCase], Command, abc.ABC
):
    """Base class for commands which require authentication."""

    _session_storage: Final[SessionStorage]
    _use_case: LoggedInMutationCommandUseCase

    def __init__(
        self, session_storage: SessionStorage, use_case: LoggedInMutationCommandUseCase
    ) -> None:
        """Constructor."""
        self._session_storage = session_storage
        self._use_case = use_case

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load()
        await self._run(session_info, args)

    @abc.abstractmethod
    async def _run(
        self,
        session: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""


LoggedInReadonlyCommandUseCase = TypeVar(
    "LoggedInReadonlyCommandUseCase", bound=AppLoggedInReadonlyUseCase[Any, Any]
)


class LoggedInReadonlyCommand(
    Generic[LoggedInReadonlyCommandUseCase], Command, abc.ABC
):
    """Base class for commands which just read and present data."""

    _session_storage: Final[SessionStorage]
    _use_case: LoggedInReadonlyCommandUseCase

    def __init__(
        self, session_storage: SessionStorage, use_case: LoggedInReadonlyCommandUseCase
    ) -> None:
        """Constructor."""
        self._session_storage = session_storage
        self._use_case = use_case

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load()
        await self._run(session_info, args)

    @abc.abstractmethod
    async def _run(
        self,
        session: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False


class TestHelperCommand(Command, abc.ABC):
    """Base class for commands used in tests."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return False

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False