"""The command for updating a slack task."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.concept.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.concept.push_integrations.slack.slack_user_name import (
    SlackUserName,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class SlackTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    user: UpdateAction[SlackUserName]
    channel: UpdateAction[SlackChannelName | None]
    message: UpdateAction[str]
    generation_name: UpdateAction[InboxTaskName | None]
    generation_status: UpdateAction[InboxTaskStatus | None]
    generation_eisen: UpdateAction[Eisen]
    generation_difficulty: UpdateAction[Difficulty]
    generation_actionable_date: UpdateAction[ADate | None]
    generation_due_date: UpdateAction[ADate | None]


@mutation_use_case(WorkspaceFeature.SLACK_TASKS)
class SlackTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[SlackTaskUpdateArgs, None]
):
    """The command for updating a slack task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SlackTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        slack_task = await uow.get_for(SlackTask).load_by_id(args.ref_id)

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

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        generated_inbox_task = (
            await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                source=[InboxTaskSource.SLACK_TASK],
                slack_task_ref_id=[slack_task.ref_id],
            )
        )[0]

        generated_inbox_task = generated_inbox_task.update_link_to_slack_task(
            ctx=context.domain_context,
            project_ref_id=generated_inbox_task.project_ref_id,
            user=slack_task.user,
            channel=slack_task.channel,
            message=slack_task.message,
            generation_extra_info=slack_task.generation_extra_info,
        )

        await uow.get_for(InboxTask).save(generated_inbox_task)
        await progress_reporter.mark_updated(generated_inbox_task)

        slack_task = slack_task.update(
            ctx=context.domain_context,
            user=args.user,
            channel=args.channel,
            message=args.message,
            generation_extra_info=generation_extra_info,
        )

        await uow.get_for(SlackTask).save(slack_task)
        await progress_reporter.mark_updated(slack_task)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: SlackTaskUpdateArgs,
        result: None,
    ) -> None:
        """Execute the command's post-mutation work."""
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.SLACK_TASKS],
            period=None,
            filter_slack_task_ref_ids=[args.ref_id],
        )
