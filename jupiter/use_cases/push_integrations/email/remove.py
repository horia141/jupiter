"""The command for hard removing a email task."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class EmailTaskRemoveUseCase(AppMutationUseCase["EmailTaskRemoveUseCase.Args", None]):
    """The command for archiving a email task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _email_task_notion_manager: Final[EmailTaskNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._email_task_notion_manager = email_task_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            email_task = uow.email_task_repository.load_by_id(ref_id=args.ref_id)

        email_task_remove_service = EmailTaskRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._email_task_notion_manager,
        )

        email_task_remove_service.do_it(progress_reporter, email_task)
