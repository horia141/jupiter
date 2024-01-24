"""UseCase for associating an inbox task with a big plan."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.associate_with_big_plan import (
    InboxTaskAssociateWithBigPlanUseCase,
)


class InboxTaskAssociateWithBigPlan(
    LoggedInMutationCommand[InboxTaskAssociateWithBigPlanUseCase]
):
    """UseCase class for associating an inbox task with a big plan."""
