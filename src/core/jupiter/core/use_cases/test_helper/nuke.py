"""The command for completely destroying a workspace."""
import logging
from typing import Final

from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.storage import Connection
from jupiter.core.framework.use_case import (
    EmptyContext,
    ProgressReporter,
    ProgressReporterFactory,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppTestHelperUseCase

LOGGER = logging.getLogger(__name__)


@use_case_args
class NukeArgs(UseCaseArgsBase):
    """Nuke args."""


class NukeUseCase(AppTestHelperUseCase[NukeArgs, None]):
    """The command for completely destroying a workspace."""

    _connection: Final[Connection]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        progress_reporter_factory: ProgressReporterFactory[EmptyContext],
        connection: Connection,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(progress_reporter_factory)
        self._connection = connection
        self._storage_engine = storage_engine

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: EmptyContext,
        args: NukeArgs,
    ) -> None:
        """Execute the command's action."""
        LOGGER.info("Daisy ... daisy ... daisy")
        self._connection.nuke()
