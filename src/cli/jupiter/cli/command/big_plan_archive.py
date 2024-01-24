"""UseCase for archiving a big plan."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.archive import (
    BigPlanArchiveArgs,
    BigPlanArchiveUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class BigPlanArchive(LoggedInMutationCommand[BigPlanArchiveUseCase]):
    """UseCase class for archiving a big plan."""
