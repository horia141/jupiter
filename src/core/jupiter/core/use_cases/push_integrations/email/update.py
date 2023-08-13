"""The command for updating a email task."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class EmailTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

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


class EmailTaskUpdateUseCase(AppLoggedInMutationUseCase[EmailTaskUpdateArgs, None]):
    """The command for updating a email task."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.EMAIL_TASKS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: EmailTaskUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            email_task = await uow.email_task_repository.load_by_id(args.ref_id)

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
                            email_task.generation_extra_info.name,
                        ),
                        status=args.generation_status.or_else(
                            email_task.generation_extra_info.status,
                        ),
                        eisen=args.generation_eisen.or_else(
                            email_task.generation_extra_info.eisen,
                        ),
                        difficulty=args.generation_difficulty.or_else(
                            email_task.generation_extra_info.difficulty,
                        ),
                        actionable_date=args.generation_actionable_date.or_else(
                            email_task.generation_extra_info.actionable_date,
                        ),
                        due_date=args.generation_due_date.or_else(
                            email_task.generation_extra_info.due_date,
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
                    filter_sources=[InboxTaskSource.EMAIL_TASK],
                    filter_email_task_ref_ids=[email_task.ref_id],
                )
            )[0]

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

            await uow.inbox_task_repository.save(generated_inbox_task)
            await progress_reporter.mark_updated(generated_inbox_task)

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

            await uow.email_task_repository.save(email_task)
            await progress_reporter.mark_updated(email_task)
