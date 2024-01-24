"""Change the project for a big plan."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.change_project import (
    BigPlanChangeProjectArgs,
    BigPlanChangeProjectUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class BigPlanChangeProject(LoggedInMutationCommand[BigPlanChangeProjectUseCase]):
    """UseCase class for hard removing big plans."""
