"""The command for updating a slack task."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
)
from jupiter.domain.push_integrations.slack.slack_channel_name import SlackChannelName
from jupiter.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SlackTaskUpdateUseCase(AppMutationUseCase["SlackTaskUpdateUseCase.Args", None]):
    """The command for updating a slack task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId
        user: UpdateAction[SlackUserName]
        channel: UpdateAction[Optional[SlackChannelName]]
        message: UpdateAction[str]
        generation_name: UpdateAction[Optional[InboxTaskName]]
        generation_status: UpdateAction[Optional[InboxTaskStatus]]
        generation_eisen: UpdateAction[Optional[Eisen]]
        generation_difficulty: UpdateAction[Optional[Difficulty]]
        generation_actionable_date: UpdateAction[Optional[ADate]]
        generation_due_date: UpdateAction[Optional[ADate]]

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
            slack_task = uow.slack_task_repository.load_by_id(args.ref_id)

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
                            slack_task.generation_extra_info.name
                        ),
                        status=args.generation_status.or_else(
                            slack_task.generation_extra_info.status
                        ),
                        eisen=args.generation_eisen.or_else(
                            slack_task.generation_extra_info.eisen
                        ),
                        difficulty=args.generation_difficulty.or_else(
                            slack_task.generation_extra_info.difficulty
                        ),
                        actionable_date=args.generation_actionable_date.or_else(
                            slack_task.generation_extra_info.actionable_date
                        ),
                        due_date=args.generation_due_date.or_else(
                            slack_task.generation_extra_info.due_date
                        ),
                    )
                )
            else:
                generation_extra_info = UpdateAction.do_nothing()

            slack_task = slack_task.update(
                user=args.user,
                channel=args.channel,
                message=args.message,
                generation_extra_info=generation_extra_info,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            uow.slack_task_repository.save(slack_task)

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            generated_inbox_task = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_sources=[InboxTaskSource.SLACK_TASK],
                filter_slack_task_ref_ids=[slack_task.ref_id],
            )[0]

            generated_inbox_task = generated_inbox_task.update_link_to_slack_task(
                project_ref_id=generated_inbox_task.project_ref_id,
                user=slack_task.user,
                channel=slack_task.channel,
                generation_extra_info=slack_task.generation_extra_info,
                message=slack_task.message,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            uow.inbox_task_repository.save(generated_inbox_task)

            project = uow.project_repository.load_by_id(
                generated_inbox_task.project_ref_id
            )

        notion_slack_task = self._slack_task_notion_manager.load_leaf(
            slack_task.slack_task_collection_ref_id, slack_task.ref_id
        )
        notion_slack_task = notion_slack_task.join_with_entity(slack_task, None)
        self._slack_task_notion_manager.save_leaf(
            slack_task.slack_task_collection_ref_id, notion_slack_task
        )

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
