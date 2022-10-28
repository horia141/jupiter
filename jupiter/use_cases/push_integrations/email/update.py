"""The command for updating a email task."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.email_address import EmailAddress
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class EmailTaskUpdateUseCase(AppMutationUseCase["EmailTaskUpdateUseCase.Args", None]):
    """The command for updating a email task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId
        from_address: UpdateAction[EmailAddress]
        from_name: UpdateAction[EmailUserName]
        to_address: UpdateAction[EmailAddress]
        subject: UpdateAction[str]
        body: UpdateAction[str]
        generation_name: UpdateAction[Optional[InboxTaskName]]
        generation_status: UpdateAction[Optional[InboxTaskStatus]]
        generation_eisen: UpdateAction[Optional[Eisen]]
        generation_difficulty: UpdateAction[Optional[Difficulty]]
        generation_actionable_date: UpdateAction[Optional[ADate]]
        generation_due_date: UpdateAction[Optional[ADate]]

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
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            email_task = uow.email_task_repository.load_by_id(args.ref_id)

            if (
                args.generation_name.should_change
                or args.generation_status.should_change
                or args.generation_eisen.should_change
                or args.generation_difficulty.should_change
                or args.generation_actionable_date.should_change
                or args.generation_due_date.should_change
            ):
                generation_extra_info = UpdateAction.change_to(
                    PushGenerationExtraInfo(
                        timezone=workspace.timezone,
                        name=args.generation_name.or_else(
                            email_task.generation_extra_info.name
                        ),
                        status=args.generation_status.or_else(
                            email_task.generation_extra_info.status
                        ),
                        eisen=args.generation_eisen.or_else(
                            email_task.generation_extra_info.eisen
                        ),
                        difficulty=args.generation_difficulty.or_else(
                            email_task.generation_extra_info.difficulty
                        ),
                        actionable_date=args.generation_actionable_date.or_else(
                            email_task.generation_extra_info.actionable_date
                        ),
                        due_date=args.generation_due_date.or_else(
                            email_task.generation_extra_info.due_date
                        ),
                    )
                )
            else:
                generation_extra_info = UpdateAction.do_nothing()

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            generated_inbox_task = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_sources=[InboxTaskSource.EMAIL_TASK],
                filter_email_task_ref_ids=[email_task.ref_id],
            )[0]

            project = uow.project_repository.load_by_id(
                generated_inbox_task.project_ref_id
            )

        with progress_reporter.start_updating_entity(
            "inbox task", generated_inbox_task.ref_id, str(generated_inbox_task.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                generated_inbox_task = generated_inbox_task.update_link_to_email_task(
                    project_ref_id=generated_inbox_task.project_ref_id,
                    from_address=email_task.from_address,
                    from_name=email_task.from_name,
                    to_address=email_task.to_address,
                    subject=email_task.subject,
                    body=email_task.body,
                    generation_extra_info=email_task.generation_extra_info,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(generated_inbox_task.name))

                uow.inbox_task_repository.save(generated_inbox_task)
                entity_reporter.mark_local_change()

            inbox_task_direct_info = NotionInboxTask.DirectInfo(
                all_projects_map={project.ref_id: project}, all_big_plans_map={}
            )
            notion_generated_inbox_task = self._inbox_task_notion_manager.load_leaf(
                generated_inbox_task.inbox_task_collection_ref_id,
                generated_inbox_task.ref_id,
            )
            notion_generated_inbox_task = notion_generated_inbox_task.join_with_entity(
                generated_inbox_task, inbox_task_direct_info
            )
            self._inbox_task_notion_manager.save_leaf(
                generated_inbox_task.inbox_task_collection_ref_id,
                notion_generated_inbox_task,
            )
            entity_reporter.mark_remote_change()

        with progress_reporter.start_updating_entity(
            "email task", email_task.ref_id, str(email_task.simple_name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                email_task = email_task.update(
                    from_address=args.from_address,
                    from_name=args.from_name,
                    to_address=args.to_address,
                    subject=args.subject,
                    body=args.body,
                    generation_extra_info=generation_extra_info,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(email_task.simple_name))

                uow.email_task_repository.save(email_task)
                entity_reporter.mark_local_change()

            notion_email_task = self._email_task_notion_manager.load_leaf(
                email_task.email_task_collection_ref_id, email_task.ref_id
            )
            notion_email_task = notion_email_task.join_with_entity(email_task, None)
            self._email_task_notion_manager.save_leaf(
                email_task.email_task_collection_ref_id, notion_email_task
            )
            entity_reporter.mark_remote_change()
