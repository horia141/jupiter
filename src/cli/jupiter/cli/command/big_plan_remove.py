"""UseCase for hard remove big plans."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.remove import (
    BigPlanRemoveArgs,
    BigPlanRemoveUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class BigPlanRemove(LoggedInMutationCommand[BigPlanRemoveUseCase]):
    """UseCase class for hard removing big plans."""
