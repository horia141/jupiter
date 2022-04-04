"""Update the slack tasks generation project."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SlackTaskChangeGenerationProjectUseCase(
    AppMutationUseCase["SlackTaskChangeGenerationProjectUseCase.Args", None]
):
    """The command for updating the generation up project for slack tasks."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        generation_project_key: Optional[ProjectKey]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _slack_task_notion_manager: Final[SlackTaskNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        slack_task_notion_manager: SlackTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._slack_task_notion_manager = slack_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )

            push_integration_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            slack_task_collection = uow.slack_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )
            old_generation_project_ref_id = (
                slack_task_collection.generation_project_ref_id
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

            slack_task_collection = slack_task_collection.change_generation_project(
                generation_project_ref_id=generation_project_ref_id,
                source=EventSource.CLI,
                modified_time=self._time_provider.get_current_time(),
            )

            uow.slack_task_collection_repository.save(slack_task_collection)

            slack_tasks = uow.slack_task_repository.find_all(
                parent_ref_id=slack_task_collection.ref_id, allow_archived=False
            )
            slack_tasks_by_ref_id = {st.ref_id: st for st in slack_tasks}

        if (
            old_generation_project_ref_id != generation_project_ref_id
            and len(slack_tasks) > 0
        ):
            with self._storage_engine.get_unit_of_work() as inbox_task_uow:
                inbox_task_collection = (
                    inbox_task_uow.inbox_task_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
                all_generated_inbox_tasks = (
                    inbox_task_uow.inbox_task_repository.find_all_with_filters(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_sources=[InboxTaskSource.SLACK_TASK],
                        filter_slack_task_ref_ids=[m.ref_id for m in slack_tasks],
                    )
                )
                updated_generated_inbox_tasks = []
                for inbox_task in all_generated_inbox_tasks:
                    slack_task = slack_tasks_by_ref_id[
                        cast(EntityId, inbox_task.slack_task_ref_id)
                    ]
                    update_inbox_task = inbox_task.update_link_to_slack_task(
                        project_ref_id=generation_project_ref_id,
                        user=slack_task.user,
                        channel=slack_task.channel,
                        generation_extra_info=slack_task.generation_extra_info,
                        message=slack_task.message,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    inbox_task_uow.inbox_task_repository.save(inbox_task)
                    updated_generated_inbox_tasks.append(update_inbox_task)

            for inbox_task in updated_generated_inbox_tasks:
                direct_info = NotionInboxTask.DirectInfo(
                    all_projects_map={generation_project.ref_id: generation_project},
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
                LOGGER.info("Applied Notion changes")
