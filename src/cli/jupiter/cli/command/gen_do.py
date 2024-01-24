"""UseCase for creating recurring tasks."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.gen.do import GenDoUseCase


class GenDo(LoggedInMutationCommand[GenDoUseCase]):
    """UseCase class for creating recurring tasks."""
