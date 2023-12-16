"""The command for updating a slack task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class SlackTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

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


class SlackTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SlackTaskUpdateArgs, None]
):
    """The command for updating a slack task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.SLACK_TASKS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: SlackTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        slack_task = await uow.slack_task_repository.load_by_id(args.ref_id)

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
                    timezone=user.timezone,
                    name=args.generation_name.or_else(
                        slack_task.generation_extra_info.name,
                    ),
                    status=args.generation_status.or_else(
                        slack_task.generation_extra_info.status,
                    ),
                    eisen=args.generation_eisen.or_else(
                        slack_task.generation_extra_info.eisen,
                    ),
                    difficulty=args.generation_difficulty.or_else(
                        slack_task.generation_extra_info.difficulty,
                    ),
                    actionable_date=args.generation_actionable_date.or_else(
                        slack_task.generation_extra_info.actionable_date,
                    ),
                    due_date=args.generation_due_date.or_else(
                        slack_task.generation_extra_info.due_date,
                    ),
                ),
            )
        else:
            generation_extra_info = UpdateAction.do_nothing()

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        generated_inbox_task = (
            await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_sources=[InboxTaskSource.SLACK_TASK],
                filter_slack_task_ref_ids=[slack_task.ref_id],
            )
        )[0]

        generated_inbox_task = generated_inbox_task.update_link_to_slack_task(
            project_ref_id=generated_inbox_task.project_ref_id,
            user=slack_task.user,
            channel=slack_task.channel,
            message=slack_task.message,
            generation_extra_info=slack_task.generation_extra_info,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.inbox_task_repository.save(generated_inbox_task)
        await progress_reporter.mark_updated(generated_inbox_task)

        slack_task = slack_task.update(
            user=args.user,
            channel=args.channel,
            message=args.message,
            generation_extra_info=generation_extra_info,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.slack_task_repository.save(slack_task)
        await progress_reporter.mark_updated(slack_task)
