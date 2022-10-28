"""Update the email tasks generation project."""
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
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


class EmailTaskChangeGenerationProjectUseCase(
    AppMutationUseCase["EmailTaskChangeGenerationProjectUseCase.Args", None]
):
    """The command for updating the generation up project for email tasks."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        generation_project_key: Optional[ProjectKey]

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
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            push_integration_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            email_task_collection = uow.email_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )
            old_generation_project_ref_id = (
                email_task_collection.generation_project_ref_id
            )

            if args.generation_project_key is not None:
                generation_project = uow.project_repository.load_by_key(
                    project_collection.ref_id, args.generation_project_key
                )
                generation_project_ref_id = generation_project.ref_id
            else:
                generation_project = uow.project_repository.load_by_id(
                    workspace.default_project_ref_id
                )
                generation_project_ref_id = workspace.default_project_ref_id

            email_tasks = uow.email_task_repository.find_all(
                parent_ref_id=email_task_collection.ref_id, allow_archived=False
            )
            email_tasks_by_ref_id = {st.ref_id: st for st in email_tasks}

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            all_generated_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.EMAIL_TASK],
                filter_email_task_ref_ids=[m.ref_id for m in email_tasks],
            )

        if (
            old_generation_project_ref_id != generation_project_ref_id
            and len(email_tasks) > 0
        ):
            updated_generated_inbox_tasks = []

            for inbox_task in all_generated_inbox_tasks:
                with progress_reporter.start_updating_entity(
                    "inbox task", inbox_task.ref_id, str(inbox_task.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as inbox_task_uow:
                        email_task = email_tasks_by_ref_id[
                            cast(EntityId, inbox_task.email_task_ref_id)
                        ]
                        update_inbox_task = inbox_task.update_link_to_email_task(
                            project_ref_id=generation_project_ref_id,
                            from_address=email_task.from_address,
                            from_name=email_task.from_name,
                            to_address=email_task.to_address,
                            subject=email_task.subject,
                            body=email_task.body,
                            generation_extra_info=email_task.generation_extra_info,
                            source=EventSource.CLI,
                            modification_time=self._time_provider.get_current_time(),
                        )
                        entity_reporter.mark_known_name(str(update_inbox_task.name))

                        inbox_task_uow.inbox_task_repository.save(inbox_task)
                        entity_reporter.mark_local_change()

                        updated_generated_inbox_tasks.append(update_inbox_task)

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={
                            generation_project.ref_id: generation_project
                        },
                        all_big_plans_map={},
                    )
                    notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    notion_inbox_task = notion_inbox_task.join_with_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.save_leaf(
                        inbox_task.inbox_task_collection_ref_id, notion_inbox_task
                    )
                    entity_reporter.mark_remote_change()

        with progress_reporter.start_updating_entity(
            "email task", email_task.ref_id, str(email_task.simple_name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                email_task_collection = email_task_collection.change_generation_project(
                    generation_project_ref_id=generation_project_ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                uow.email_task_collection_repository.save(email_task_collection)
                entity_reporter.mark_local_change()
